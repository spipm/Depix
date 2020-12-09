# Depix

[English](./README.md) | [中文](./README_zh-cn.md)

`Depix` 是一个用来从被打码的截图中恢复密码的工具。——可以处理用线性框过滤器创建的像素化图像。

在[这篇文章](https://www.linkedin.com/pulse/recovering-passwords-from-pixelized-screenshots-sipke-mellema)中我讲了一些马赛克背景知识以及相似的研究。

### 🔮 例子

`python depix.py -p images/testimages/testimage3_pixels.png -s images/searchimages/debruinseq_notepad_Windows10_closeAndSpaced.png -o output.png`

![image](docs/img/Recovering_prototype_latest.png)

### 👉 使用

1. 把打码部分从截图中截成一个长方形图片；
2. 使用预期字符粘贴一个[De Bruijn sequence](https://damip.net/article-de-bruijn-sequence)在具有相同字体设置（文本大小、字体、颜色、hsl）的编辑器中；
3. 给那个序列截一个图，最好使用和你生成那个马赛克相同的工具；
4. 运行`python depix.py -p [pixelated rectangle image] -s [search sequence image] -o output.png` 

### 🧮 算法

该算法利用了线性盒式滤波器分别处理每个块的原理。对于每个块，它将搜索图像中的所有像素化的块以检查是否直接匹配。

对于大多数像素化的图像，Depix 能够找到单一匹配结果，然后假设这些结果是正确的。然后将周围多个匹配块的匹配在几何上与像素化图像中相同的距离进行比较，匹配结果也被视为正确。这个过程会重复几次。

当正确的块不再有几何匹配后，它将直接输出所有正确的图块。对于多匹配块，它输出所有匹配块的平均值。

### 🗑 杂项



### ⁇ 使用 issues

* **依赖问题** 查看: https://github.com/beurtschipper/Depix/issues/12
