from torch.utils.data import DataLoader, TensorDataset
from torch.optim.lr_scheduler import ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from .Transformer import Transformer
from utils.logger import Logger
import pandas_ta as ta
import pandas as pd
import numpy as np
import datetime
import torch
import os

import warnings
warnings.filterwarnings("ignore")
logger = Logger()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
learning_rate = 1e-4
batch_size = 128
epochs = 100

# 以项目路径为根目录
model_dir = './model'
os.makedirs(model_dir, exist_ok=True)

class Normalizer():
    def __init__(self):
        self.mu = None
        self.sd = None

    def fit_transform(self, x):
        self.mu = np.mean(x, axis=0, keepdims=True)
        self.sd = np.std(x, axis=0, keepdims=True)
        normalized_x = (x - self.mu) / self.sd
        return normalized_x

    def inverse_transform(self, x):
        return (x * self.sd) + self.mu

def transformerLoadDataset(data, batch_size, window_size=25):
    #  针对交易时间进行排序，并进行补充维度的添加
    data.ta.macd(append=True)
    data.ta.rsi(append=True)
    data = data.dropna()

    # 数据的特征处理
    features = ['close', 'high', 'low', 'open', 'vol', 'MACD_12_26_9', 'RSI_14']
    data = data[features]
    data_values = data.values.astype(np.float32)

    normalizer = Normalizer()
    data_normalized = normalizer.fit_transform(data_values)

    # 滑动窗口切割
    X_windows = []
    y_windows = []
    for i in range(len(data_normalized) - window_size):
        X_windows.append(data_normalized[i:i + window_size, :])
        y_windows.append(data_normalized[i + window_size, 0])

    # 将窗口数据转换为PyTorch张量
    X_windows = torch.tensor(X_windows, dtype=torch.float32)
    y_windows = torch.tensor(y_windows, dtype=torch.float32).unsqueeze(-1)

    # 分割训练集和验证集
    X_train, X_val, y_train, y_val = train_test_split(
        X_windows, y_windows,
        test_size=0.2, shuffle=False,
        random_state= 42
    )

    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_val, y_val)
    train_loader = DataLoader(train_dataset, batch_size, shuffle=False)
    val_loader = DataLoader(val_dataset, batch_size, shuffle=False)

    return train_loader, val_loader, data

def train(stock_code, data):
    # 获取训练和验证数据集
    train_dataloader, val_dataloader, data = transformerLoadDataset(data, batch_size)

    # 初始化模型、损失函数和优化器
    model = Transformer().to(device)
    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=5)

    logger.info(f"Initialization is complete.Training model{stock_code} begins")
    best_loss = float('inf')
    for epoch in range(epochs):
        # 训练阶段
        model.train()

        for X_batch, y_batch in train_dataloader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)

            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()

        # 每五轮进行一次验证
        avg_val_loss = None
        if (epoch + 1) % 5 == 0:
            model.eval()

            val_loss = []
            with torch.no_grad():
                for X_batch, y_batch in val_dataloader:
                    X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                    outputs = model(X_batch)
                    loss = criterion(outputs, y_batch)

                    val_loss.append(loss.item())

            avg_val_loss = np.mean(val_loss)

            # 根据验证机的损失更新调度器，调整学习率
            scheduler.step(avg_val_loss)

        if avg_val_loss is not None and avg_val_loss < best_loss:
            best_loss = avg_val_loss
            model_path = os.path.join(
                model_dir,
                f"{stock_code}_best_model.pth"
            )
            torch.save(model.state_dict(), model_path)
    logger.info(f'Training complete.The smallest verification loss is:{best_loss}')
    return data

def forecast(stock_code, data):
    # 加载模型参数
    model = Transformer().to(device)
    model.load_state_dict(torch.load(os.path.join(model_dir, f"{stock_code}_best_model.pth")))
    model.eval()

    # 构造预测数据
    normalizer = Normalizer()
    latest_data = data.values[-25:].astype(np.float32)
    latest_data = normalizer.fit_transform(latest_data)
    latest_data = torch.tensor(latest_data, dtype=torch.float32).unsqueeze(0) # (1, window_size, num_features)

    with torch.no_grad():
        prediction = model(latest_data.to(device))

    prediction = normalizer.inverse_transform(prediction.cpu().numpy())
    return prediction