# -*- coding: utf-8 -*-
import json
import os
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from torchvision import datasets, transforms

WORK = r"C:\Users\86136\Desktop\深度学习实验四_MLP"
FIG = os.path.join(WORK, "figs")
os.makedirs(FIG, exist_ok=True)

torch.manual_seed(0)
np.random.seed(0)

batch_size = 2048
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device:", device, torch.cuda.get_device_name(0) if torch.cuda.is_available() else "")

train_set = datasets.MNIST(r"C:\Users\86136\data", train=True, download=False,
                           transform=transforms.Compose([transforms.ToTensor()]))
test_set = datasets.MNIST(r"C:\Users\86136\data", train=False, download=False,
                          transform=transforms.Compose([transforms.ToTensor()]))
train_loader = torch.utils.data.DataLoader(train_set, batch_size=batch_size, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_set, batch_size=batch_size, shuffle=False)
print("train", train_set.data.shape, "test", test_set.data.shape)


class mlp(nn.Module):
    def __init__(self):
        super(mlp, self).__init__()
        self.l1 = nn.Linear(784, 128)
        self.l2 = nn.Linear(128, 10)

    def forward(self, x):
        a1 = self.l1(x)
        x1 = F.relu(a1)
        a2 = self.l2(x1)
        return a2


model = mlp().to(device)
optimizer = optim.SGD(model.parameters(), lr=0.01)
print(model)

epochs = 30
hist = {"train_loss": [], "train_acc": [], "test_loss": [], "test_acc": [], "time": []}
t0 = time.time()
for epoch in range(epochs):
    model.train()
    run_loss, run_correct, run_n = 0.0, 0, 0
    for batch_idx, (x, y) in enumerate(train_loader):
        x, y = x.view(x.shape[0], -1).to(device), y.to(device)
        optimizer.zero_grad()
        output = model(x)
        loss = F.cross_entropy(output, y)
        loss.backward()
        optimizer.step()
        run_loss += loss.item() * y.size(0)
        run_correct += output.argmax(1).eq(y).sum().item()
        run_n += y.size(0)

    tr_loss = run_loss / run_n
    tr_acc = run_correct / run_n

    model.eval()
    correct, test_loss, total = 0, 0.0, 0
    all_pred, all_true = [], []
    with torch.no_grad():
        for x, y in test_loader:
            x, y = x.view(x.shape[0], -1).to(device), y.to(device)
            output = model(x)
            test_loss += F.cross_entropy(output, y, reduction="sum").item()
            pred = output.max(1, keepdim=True)[1]
            correct += pred.eq(y.view_as(pred)).sum().item()
            total += y.size(0)
            all_pred.append(pred.view(-1).cpu())
            all_true.append(y.cpu())
    te_loss = test_loss / total
    te_acc = correct / total

    hist["train_loss"].append(tr_loss)
    hist["train_acc"].append(tr_acc)
    hist["test_loss"].append(te_loss)
    hist["test_acc"].append(te_acc)
    hist["time"].append(time.time() - t0)
    print("epoch:{:2d}  train_loss:{:.4f}  train_acc:{:.4f}  test_loss:{:.4f}  test_acc:{:.4f}".format(
        epoch, tr_loss, tr_acc, te_loss, te_acc))

pred = torch.cat(all_pred).numpy()
true = torch.cat(all_true).numpy()

cm = np.zeros((10, 10), dtype=int)
for t, p in zip(true, pred):
    cm[t, p] += 1
per_class = (cm.diagonal() / cm.sum(axis=1)).tolist()

print("final test acc:", round(float(te_acc), 4))
print("per class acc:", [round(v, 4) for v in per_class])
print("params:", sum(p.numel() for p in model.parameters()))
print("total time %.1fs" % (time.time() - t0))

# ---------- 图1 样本 ----------
x_show, y_show = next(iter(torch.utils.data.DataLoader(train_set, batch_size=64, shuffle=True)))
fig, axes = plt.subplots(4, 8, figsize=(8.0, 4.2))
for i, ax in enumerate(axes.ravel()):
    ax.imshow(x_show[i].squeeze(0).numpy(), cmap="gray")
    ax.set_title(str(int(y_show[i])), fontsize=9)
    ax.axis("off")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig1_samples.png"), bbox_inches="tight", dpi=200)
plt.close()

# ---------- 图2 训练曲线 ----------
ep = np.arange(1, epochs + 1)
fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.4))
ax[0].plot(ep, hist["train_loss"], color="#0072B2", lw=1.6, label="Train loss")
ax[0].plot(ep, hist["test_loss"], color="#D55E00", lw=1.6, ls="--", label="Test loss")
ax[0].set_xlabel("Epoch")
ax[0].set_ylabel("Cross-entropy loss")
ax[0].set_title("Loss Curves", fontsize=10)
ax[0].legend(frameon=False, fontsize=9)
ax[0].grid(alpha=0.25, ls=":")
ax[1].plot(ep, np.array(hist["train_acc"]) * 100, color="#0072B2", lw=1.6, label="Train acc")
ax[1].plot(ep, np.array(hist["test_acc"]) * 100, color="#D55E00", lw=1.6, ls="--", label="Test acc")
ax[1].set_xlabel("Epoch")
ax[1].set_ylabel("Accuracy (%)")
ax[1].set_title("Accuracy Curves", fontsize=10)
ax[1].legend(frameon=False, fontsize=9)
ax[1].grid(alpha=0.25, ls=":")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig2_curves.png"), bbox_inches="tight", dpi=200)
plt.close()

# ---------- 图3 预测示例 ----------
idx = np.random.RandomState(3).choice(len(true), 32, replace=False)
fig, axes = plt.subplots(4, 8, figsize=(9.0, 4.8))
for ax, k in zip(axes.ravel(), idx):
    ax.imshow(test_set.data[k].numpy(), cmap="gray")
    ok = pred[k] == true[k]
    ax.set_title("%d / %d" % (pred[k], true[k]), fontsize=9,
                 color="#009E73" if ok else "#D55E00")
    ax.axis("off")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig3_predictions.png"), bbox_inches="tight", dpi=200)
plt.close()

# ---------- 图4 混淆矩阵 ----------
fig, ax = plt.subplots(figsize=(4.8, 4.2))
im = ax.imshow(cm, cmap="Blues")
for i in range(10):
    for j in range(10):
        if cm[i, j]:
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=7,
                    color="white" if cm[i, j] > cm.max() * 0.5 else "#333333")
ax.set_xticks(range(10))
ax.set_yticks(range(10))
ax.set_xlabel("Predicted label")
ax.set_ylabel("True label")
ax.set_title("Confusion Matrix on Test Set", fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig4_confusion.png"), bbox_inches="tight", dpi=200)
plt.close()

out = {
    "device": str(device),
    "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "",
    "torch": torch.__version__,
    "batch_size": batch_size,
    "lr": 0.01,
    "epochs": epochs,
    "params": int(sum(p.numel() for p in model.parameters())),
    "history": hist,
    "final": {"test_loss": float(te_loss), "test_acc": float(te_acc),
              "train_loss": float(tr_loss), "train_acc": float(tr_acc)},
    "per_class_acc": [float(v) for v in per_class],
    "confusion": cm.tolist(),
    "first10": hist["test_acc"][:10],
}
with open(os.path.join(WORK, "results.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("saved results.json")
