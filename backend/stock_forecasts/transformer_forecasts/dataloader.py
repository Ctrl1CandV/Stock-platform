from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
import pandas_ta as ta
import pandas as pd
import numpy as np
import torch

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
    data['trade_date'] = pd.to_datetime(data['trade_date'])
    data.set_index('trade_date', inplace=True)
    data = data.sort_index(ascending=True)
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

    return train_loader, val_loader