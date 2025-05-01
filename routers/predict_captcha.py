import torch
import torch.nn as nn
from PIL import Image
import torchvision.transforms as transforms
import string
import os

# 字元映射
CHARS = string.digits + string.ascii_letters
IDX2CHAR = {i: c for i, c in enumerate(CHARS)}
NUM_CLASSES = len(CHARS) + 1  # +1 for CTC blank

# 模型架構（與訓練時相同）
class CRNN(nn.Module):
    def __init__(self, num_classes):
        super(CRNN, self).__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 64, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(128, 256, 3, padding=1), nn.ReLU(),
            nn.Conv2d(256, 256, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d((2, 1), (2, 1)),
            nn.Conv2d(256, 512, 3, padding=1),
            nn.BatchNorm2d(512), nn.ReLU(),
            nn.Conv2d(512, 512, 3, padding=1),
            nn.BatchNorm2d(512), nn.ReLU(),
            nn.MaxPool2d((2, 1), (2, 1))
        )
        self.rnn1 = nn.LSTM(512 * 3, 256, bidirectional=True, batch_first=True)
        self.rnn2 = nn.LSTM(512, 256, bidirectional=True, batch_first=True)
        self.fc = nn.Linear(512, num_classes)

    def forward(self, x):
        x = self.cnn(x)
        b, c, h, w = x.size()
        x = x.permute(0, 3, 1, 2)
        x = x.reshape(b, w, c * h)
        x, _ = self.rnn1(x)
        x, _ = self.rnn2(x)
        x = self.fc(x)
        x = x.permute(1, 0, 2)
        return x

# CTC 解碼器（簡單 greedy decode）
def ctc_decode(output):
    preds = torch.argmax(output, dim=2)
    preds = preds.permute(1, 0)  # [B, T]
    texts = []
    for pred in preds:
        text = ""
        prev = -1
        for p in pred:
            p = p.item()
            if p != prev and p != NUM_CLASSES - 1:
                text += IDX2CHAR[p]
            prev = p
        texts.append(text)
    return texts
def preprocess_and_ocr(image):
    # 圖片前處理
    transform = transforms.Compose([
        transforms.Grayscale(),
        transforms.Resize((60, 160)),
        transforms.ToTensor()
    ])

    # 載入模型
    model = CRNN(NUM_CLASSES)
    
    model_path = os.path.join(os.path.dirname(__file__), "captcha_model.pt")
    torch.load(model_path, map_location="cpu")
    model.load_state_dict(torch.load("captcha_model.pt", map_location="cpu"))
    model.eval()

    # 載入要預測的圖片
    image = image.convert("RGB")
    image = transform(image).unsqueeze(0)  # [1, 1, 60, 160]

    # 預測
    with torch.no_grad():
        output = model(image)
        result = ctc_decode(output)

    print("🧠 模型預測結果:", result[0])
    return result[0]
