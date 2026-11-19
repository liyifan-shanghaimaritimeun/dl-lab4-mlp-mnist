# -*- coding: utf-8 -*-
import json
import os

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

WORK = r"C:\Users\86136\Desktop\深度学习实验四_MLP"
FIG = os.path.join(WORK, "figs")
OUT = os.path.join(WORK, "深度学习实验四-多层感知机-李铱璠.docx")

with open(os.path.join(WORK, "results.json"), encoding="utf-8") as f:
    R = json.load(f)

doc = Document()
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.left_margin = Cm(3.17)
sec.right_margin = Cm(3.17)
sec.top_margin = Cm(2.54)
sec.bottom_margin = Cm(2.54)

normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(12)
normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


def set_run_font(run, ascii_font="Times New Roman", east="宋体", size=12, bold=None):
    run.font.name = ascii_font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), east)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold


def para(text="", size=12, bold=False, align=None, indent=True,
         before=0, after=0, line=1.5, ascii_font="Times New Roman", east="宋体"):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if indent:
        pf.first_line_indent = Pt(size * 2)
    if align is not None:
        p.alignment = align
    if text:
        r = p.add_run(text)
        set_run_font(r, ascii_font, east, size, bold)
    return p


def title(text):
    return para(text, size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
                indent=False, before=0, after=12, line=1.3)


def heading(text, before=10, after=4):
    return para(text, size=12, bold=True, indent=False,
                before=before, after=after, line=1.5)


def body(text):
    return para(text, size=12, indent=True, before=0, after=0, line=1.5)


def code(lines):
    for i, ln in enumerate(lines):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.first_line_indent = Pt(0)
        pf.left_indent = Cm(0.6)
        pf.space_before = Pt(4 if i == 0 else 0)
        pf.space_after = Pt(4 if i == len(lines) - 1 else 0)
        pf.line_spacing = 1.0
        r = p.add_run(ln if ln else " ")
        set_run_font(r, "Consolas", "宋体", 9)


def figure(name, caption, width_cm=14.2):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = p.paragraph_format
    pf.first_line_indent = Pt(0)
    pf.space_before = Pt(6)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.0
    pf.keep_with_next = True
    p.add_run().add_picture(os.path.join(FIG, name), width=Cm(width_cm))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.first_line_indent = Pt(0)
    cap.paragraph_format.space_before = Pt(0)
    cap.paragraph_format.space_after = Pt(10)
    cap.paragraph_format.line_spacing = 1.0
    r = cap.add_run(caption)
    set_run_font(r, "Times New Roman", "宋体", 10.5, False)


def _border(tag, sz):
    el = OxmlElement(tag)
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(sz))
    el.set(qn("w:space"), "0")
    el.set(qn("w:color"), "000000")
    return el


def _none(tag):
    el = OxmlElement(tag)
    el.set(qn("w:val"), "none")
    el.set(qn("w:sz"), "0")
    el.set(qn("w:space"), "0")
    el.set(qn("w:color"), "auto")
    return el


def table(caption, header, rows, widths):
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.first_line_indent = Pt(0)
    cap.paragraph_format.space_before = Pt(8)
    cap.paragraph_format.space_after = Pt(3)
    cap.paragraph_format.line_spacing = 1.0
    cap.paragraph_format.keep_with_next = True
    r = cap.add_run(caption)
    set_run_font(r, "Times New Roman", "宋体", 10.5, False)

    t = doc.add_table(rows=len(rows) + 1, cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tblPr = t._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    borders.append(_border("w:top", 12))
    borders.append(_none("w:left"))
    borders.append(_border("w:bottom", 12))
    borders.append(_none("w:right"))
    borders.append(_none("w:insideH"))
    borders.append(_none("w:insideV"))
    tblPr.append(borders)

    all_rows = [header] + rows
    for i, row in enumerate(all_rows):
        tr = t.rows[i]
        for j, val in enumerate(row):
            cell = tr.cells[j]
            cell.width = Cm(widths[j])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(str(val))
            set_run_font(r, "Times New Roman", "宋体", 10.5, i == 0)
        if i == 0:
            for cell in tr.cells:
                tcPr = cell._tc.get_or_add_tcPr()
                tcB = OxmlElement("w:tcBorders")
                tcB.append(_border("w:bottom", 6))
                tcPr.append(tcB)

    tail = doc.add_paragraph()
    tail.paragraph_format.space_before = Pt(0)
    tail.paragraph_format.space_after = Pt(0)
    tail.paragraph_format.line_spacing = 1.0


# ---------------- 正文 ----------------
title("实验名称：多层感知机实现MNIST手写数字识别")
para("姓名：李铱璠　学号：202410315057　班级：人工智能242",
     size=12, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, after=14, line=1.3)

heading("一、实验目的", before=6)
body("1.理解多层感知机的基本结构，掌握输入层、隐藏层和输出层之间的维度关系，以及ReLU激活函数引入非线性的作用。")
body("2.学会用PyTorch搭建全连接网络，定义交叉熵损失和SGD优化器，完成一个完整的训练循环。")
body("3.在MNIST手写数字数据集上完成训练和测试，能读懂训练曲线、混淆矩阵和逐类别准确率，并对结果做出解释。")

heading("二、实验内容")
body("实验按参考代码的顺序进行：先加载并预处理MNIST数据集，再定义一个含单隐藏层的MLP，用交叉熵损失和SGD训练30轮，最后在测试集上计算准确率并做可视化分析。全部代码在CUDA环境下运行，所用显卡为NVIDIA GeForce RTX 3050 Laptop GPU，PyTorch版本为2.6.0+cu124。")

heading("2.1 数据集加载与预处理", before=8, after=3)
body("MNIST训练集有60000张28×28的灰度图，测试集有10000张，共10个类别。预处理只做ToTensor，把像素值从0~255缩放到0~1的浮点张量；送入网络前再用view把每张图拉平成784维向量，与第一层全连接的输入维度对应。批大小取2048，训练集每个epoch前打乱，测试集不打乱，保证评估结果可复现。")
code([
    "batch_size = 2048",
    "device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')",
    "",
    "train_loader = torch.utils.data.DataLoader(",
    "    datasets.MNIST('data', train=True, download=True,",
    "                   transform=transforms.Compose([transforms.ToTensor()])),",
    "    batch_size=batch_size, shuffle=True)",
    "",
    "test_loader = torch.utils.data.DataLoader(",
    "    datasets.MNIST('data', train=False,",
    "                   transform=transforms.Compose([transforms.ToTensor()])),",
    "    batch_size=batch_size, shuffle=False)",
])

heading("2.2 网络结构", before=8, after=3)
body("网络只有两层全连接。第一层把784维输入压到128维，接ReLU把负值置零；第二层再把128维映射到10维，输出对应0~9的logits。因为交叉熵损失内部会做softmax，前向传播里不再手动加softmax。")
code([
    "class mlp(nn.Module):",
    "    def __init__(self):",
    "        super(mlp, self).__init__()",
    "        self.l1 = nn.Linear(784, 128)",
    "        self.l2 = nn.Linear(128, 10)",
    "",
    "    def forward(self, x):",
    "        a1 = self.l1(x)",
    "        x1 = F.relu(a1)",
    "        a2 = self.l2(x1)",
    "        return a2",
])
body("按层统计参数量：第一层784×128+128=100480，第二层128×10+10=1290，合计101770个可训练参数。这个规模很小，单卡训练一轮不到10秒。")

heading("2.3 训练过程", before=8, after=3)
body("损失函数用交叉熵，优化器用SGD，学习率0.01，共训练30轮。每个batch依次执行梯度清零、前向计算、求损失、反向传播和参数更新。训练时把数据和标签都搬到GPU上，同时累加损失和预测正确的数量，用来统计本轮的平均损失和训练准确率。")
code([
    "model = mlp().to(device)",
    "optimizer = optim.SGD(model.parameters(), lr=0.01)",
    "",
    "for epoch in range(30):",
    "    model.train()",
    "    for batch_idx, (x, y) in enumerate(train_loader):",
    "        x, y = x.view(x.shape[0], -1).to(device), y.to(device)",
    "        optimizer.zero_grad()",
    "        output = model(x)",
    "        loss = F.cross_entropy(output, y)",
    "        loss.backward()",
    "        optimizer.step()",
])
body("30轮训练总耗时约252.5秒，平均每轮8.4秒。训练过程中每轮结束后立刻在测试集上评估一次，这样能直接看到模型在未见数据上的表现，而不只是训练集上的拟合情况。")

heading("2.4 测试与评估", before=8, after=3)
body("评估前先调用model.eval()切到评估模式，并用torch.no_grad()关闭计算图，减少显存占用。每批数据取logits中最大值的下标作为预测类别，与真实标签比较后累加正确数。同时把全部预测结果和真实标签保存下来，用于后面画混淆矩阵和逐类别准确率。")
code([
    "model.eval()",
    "correct, test_loss, total = 0, 0.0, 0",
    "with torch.no_grad():",
    "    for x, y in test_loader:",
    "        x, y = x.view(x.shape[0], -1).to(device), y.to(device)",
    "        output = model(x)",
    "        test_loss += F.cross_entropy(output, y, reduction='sum').item()",
    "        pred = output.max(1, keepdim=True)[1]",
    "        correct += pred.eq(y.view_as(pred)).sum().item()",
    "        total += y.size(0)",
    "test_acc = correct / total",
])

heading("2.5 结果可视化", before=8, after=3)
body("为了检查数据和训练效果，画了四张图：训练集样本、损失与准确率曲线、测试集预测示例、测试集混淆矩阵。四张图都由run_mlp.py在同一次运行中生成，数据来源为本地MNIST数据集。")

figure("fig1_samples.png", "图1  MNIST训练集样本示例（标题为真实标签）", 13.0)
body("图1随机抽取了训练集中的32张图片，按4行8列排布，每张图上方的数字是真实标签。样本以黑底白字为主，书写风格差异明显，有的笔画很细，有的连笔严重，这些差异正是后面分类出错的主要来源。")

figure("fig2_curves.png", "图2  30轮训练与测试的损失、准确率曲线", 15.0)
body("图2左边是损失曲线，右边是准确率曲线，蓝色实线为训练集，橙色虚线为测试集。两条曲线走势基本重合，说明模型没有出现明显的过拟合。第1轮测试准确率只有32.81%，到第10轮升到76.29%，第20轮为83.61%，第30轮达到86.15%。前10轮提升最快，之后曲线逐渐变平，继续增加轮数带来的收益已经很小。")

figure("fig3_predictions.png", "图3  测试集预测示例（标题为“预测/真实”，绿色正确、橙色错误）", 14.6)
body("图3从测试集中随机抽取32张图片，标题左边是模型预测，右边是真实标签。大部分标题是绿色，说明预测正确；少数橙色标题对应分错的样本，基本都是笔画粘连或写法不规范的数字，人眼辨认也需要多看几眼。")

figure("fig4_confusion.png", "图4  测试集混淆矩阵（行为真实标签，列为预测标签）", 11.0)
body("图4对角线上的数值越大表示该类分得越准。可以直观看到5这一行明显偏暗，有92张被错判成3，52张被判成8，38张被判成6；4和9之间也有较多互相混淆，4被判成9有82张，9被判成4有85张。0和1两类的对角线最深，几乎全部分对。")

heading("三、实验结果与分析")
heading("3.1 总体结果", before=8, after=3)
table("表1  模型在训练集和测试集上的最终结果",
      ["指标", "数值"],
      [["训练损失", "0.6272"],
       ["训练准确率", "85.49%"],
       ["测试损失", "0.5994"],
       ["测试准确率", "86.15%"],
       ["可训练参数量", "101770"],
       ["训练总耗时", "252.5 s"]],
      [7.0, 5.0])
body("表1汇总了训练结束时的指标。测试损失略低于训练损失，测试准确率比训练准确率高0.66个百分点，这主要是因为训练阶段统计的是整个epoch内各batch的滑动平均，前期准确率较低的部分也被算了进去，而测试是在训练完一轮后统一评估的。两者差距很小，可以认为模型拟合正常，没有过拟合。")

heading("3.2 训练曲线分析", before=8, after=3)
body("从图2看，损失在前10轮下降很快，训练损失从2.273降到1.498，测试损失从2.240降到1.432；第10轮以后下降速度明显放缓，最后10轮训练损失只从1.498降到0.627。准确率的增长也遵循同样的规律，前10轮从32.81%涨到76.29%，后20轮一共只涨了约10个百分点。这说明在固定学习率0.01的SGD下，模型已经接近当前结构能达到的水平，想让曲线继续下降需要调整学习率或增加网络容量。")

heading("3.3 逐类别准确率", before=8, after=3)
pc = R["per_class_acc"]
cm = R["confusion"]
rows = []
for i in range(10):
    err = sum(cm[i]) - cm[i][i]
    rows.append([str(i), "%.2f%%" % (pc[i] * 100), str(err)])
table("表2  测试集各类别的准确率与错误数",
      ["类别", "准确率", "错误数"],
      rows,
      [3.6, 4.4, 3.6])
body("表2给出了每一类的准确率。0和1最高，分别为96.53%和96.48%；5最低，只有68.16%，892张测试图里错了284张。2、8、9三类的准确率也在81%~82%之间，属于第二梯队。这个结果和混淆矩阵一致：数字5的写法变化大，上半部分容易写成3的形状，下半部分的弯钩又容易和8、6混淆。")
body("另一个明显的混淆对是4和9。4的右侧竖线和9的左侧圈在低分辨率下很接近，加上部分样本写得比较潦草，模型仅凭784个像素的线性组合很难区分。0和1的笔画结构简单、方向明确，所以准确率最高。")

heading("3.4 结果讨论", before=8, after=3)
body("这个模型的结构非常简单，只有一层128维的隐藏层，参数量约10万，最终测试准确率86.15%。作为入门实验，这个结果说明MLP确实能从像素中学习到数字的类别特征，但也暴露出两个问题：一是全连接层把图像拉平后丢失了二维空间结构，相邻像素的关系没有被利用；二是单隐藏层的表达能力有限，对写法差异大的类别不够敏感。")
body("如果要继续提升，可以从几个方向尝试：增加隐藏层或隐藏单元数量，换用Adam等自适应优化器并配合学习率衰减，加入Dropout或权重衰减抑制过拟合，或者直接改用卷积神经网络，让网络自己学习局部纹理特征。对本实验而言，这些改动不属于参考代码的范围，这里只作为后续改进的方向。")

heading("四、实验小结", before=8, after=3)
body("这次实验把PyTorch训练一个分类模型的完整流程走了一遍。数据加载部分要注意把28×28的图片拉平成784维，否则全连接层会报维度不匹配；训练部分最容易漏的是optimizer.zero_grad()，不清梯度会导致梯度累加，损失曲线会异常；评估部分则要记得切到eval模式并关闭计算图。")
body("跑完30轮用了大约4分钟，最终测试准确率86.15%。从混淆矩阵看，错误主要集中在5、4、9这些容易写混的数字上，而0和1几乎不会分错。对比实验一的线性模型，MLP加了ReLU之后确实能拟合更复杂的边界，但因为丢掉了图像的空间结构，效果离卷积网络还有明显差距。这为后面学习CNN提供了一个很直接的对照。")

doc.save(OUT)
print("saved:", OUT)
