from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.tensorboard import SummaryWriter
from dataloader import transformerLoadDataset
from Transformer import Transformer
from tqdm import tqdm
import numpy as np
import datetime
import torch
import os

import warnings
warnings.filterwarnings("ignore")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
learning_rate = 1e-4
batch_size = 128
epochs = 100

def main(stock_code, data):
    model_dir = './model'
    os.makedirs(model_dir, exist_ok=True)

    # 获取训练和验证数据集
    train_dataloader, val_dataloader = transformerLoadDataset(data, batch_size)
    print("The data is loaded")

    # 初始化模型、损失函数和优化器
    model = Transformer().to(device)
    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=5)
    print("The model and training tools are initialized")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    writer = SummaryWriter(f'runs/transformer_{timestamp}')

    print("Training begins")
    best_loss = float('inf')
    for epoch in range(epochs):
        # 训练阶段
        model.train()
        epoch_progress = tqdm(
            desc=f"Epoch {epoch + 1}/{epochs} [Train]",
            total=len(train_dataloader),
            position=0
        )

        train_loss = []
        for X_batch, y_batch in train_dataloader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)

            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()

            train_loss.append(loss.item())
            epoch_progress.set_postfix({'Loss': f"{loss.item():.4f}"})
            epoch_progress.update()

        epoch_progress.close()
        avg_train_loss = np.mean(train_loss)
        writer.add_scalar('Loss/train', avg_train_loss, epoch)

        # 每五轮进行一次验证
        avg_val_loss = None
        if (epoch + 1) % 5 == 0:
            model.eval()
            val_progress = tqdm(
                desc=f"Epoch {epoch + 1}/{epochs} [Val]",
                total=len(val_dataloader),
                position=0
            )

            val_loss = []
            with torch.no_grad():
                for X_batch, y_batch in val_dataloader:
                    X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                    outputs = model(X_batch)
                    loss = criterion(outputs, y_batch)

                    val_loss.append(loss.item())
                    val_progress.set_postfix({'Loss': f"{loss.item():.4f}"})
                    val_progress.update()

            val_progress.close()
            avg_val_loss = np.mean(val_loss)
            writer.add_scalar('Loss/val', avg_val_loss, epoch)

            # 根据验证机的损失更新调度器，调整学习率
            scheduler.step(avg_val_loss)

        if avg_val_loss is not None and avg_val_loss < best_loss:
            best_loss = avg_val_loss
            model_path = os.path.join(
                model_dir,
                f"{stock_code}_best_model_{timestamp}.pth"
            )
            torch.save(model.state_dict(), model_path)
            tqdm.write(f"Saved best model with val loss: {avg_val_loss:.4f}")

        log_msg = f"Epoch [{epoch + 1}/{epochs}] | Train Loss: {avg_train_loss:.4f}"
        if avg_val_loss is not None:
            log_msg += f" | Val Loss: {avg_val_loss:.4f}"
        tqdm.write(log_msg)

    writer.close()
    print('Training complete')


if __name__ == '__main__':
    import tushare as ts

    token = '66e72ae286def4e5826d1edc84f45cdad596c34137a91396b335cefd'
    pro = ts.pro_api(token)

    stock_code = '301091.SZ'
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=500)
    start_date, end_date = start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')
    data = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
    main(stock_code, data)