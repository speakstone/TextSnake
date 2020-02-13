

# 文本检测

Author：Face++



## 0. 研究目的

1.基于轴对齐方式的矩形框，只对水平和竖直的文本奏效，对于倾斜，弯折，曲面的文本，会引入好多背景无关区域。

2.基于旋转的矩形框，也就是加入了角度。可以适应于倾斜的文本，但是对于弯折，曲面的文本还是回引入背景无关区域。

3.基于凸四边形的方法，依然对曲面，弯折的文本无法适应。

## 1. 目标愿景

以解决水平、多方向和<font color="#dd0000">弯曲</font> 的文本检测。

<div style="color:#0000FF" align="center">
<img src="http://princepicbed.oss-cn-beijing.aliyuncs.com/blog_20181228172334.png" width="530"/> 
</div>

## 2. 算法原理

### 2.1 基本思想

<div style="color:#0000FF" align="center">
<img src="http://princepicbed.oss-cn-beijing.aliyuncs.com/blog_20181228172346.png" width="530"/> 
</div>

利用多个可变的有序圆盘disk(<font color="#0000dd">蓝色</font>）按照中心线TCL（<font color="#00dd00">绿色</font>）方向滑动连接整个文本区域TR（<font color="#dddd00">黄色</font>），圆盘的几何形状与半径r和方位θ相关联。其与传统的表征方式(轴对齐矩形、旋转矩形和四边形)相比，不考虑文本区域的形状和长度。

注意：<font color="#dd0000">disk与文本并非一一对应</font>，感觉基本的思想就是滑动窗口沿着中心线连接整个文本区域，从而解决曲面文本问题。从而引出一些问题：中心线如何确定？disk数目和大小如何确定？如何连接disk？

### 2.2 Feature map

<div style="color:#0000FF" align="center">
<img src="demo\Fig3.png" width="530"/> 
</div>

采用了FCN来预测文本实例的几何属性（7个特征图），包括2个文本区域TR(text regions),2个文本中心线TCL(text center line)，1个圆环的半径radius，一个角度的余弦值cosθ，一个角度的正弦值sinθ。 由于TCL是TR的一部分，因此TR的映射会进一步覆盖TCL映射。考虑到TCL彼此不重叠的事实，使用不相交集来执行实例分割。使用跨步运算用于提取中心轴点列表（中心线）并最终重建文本实例。

### 2.3 网络结构

<div style="color:#0000FF" align="center">
<img src="demo\Fig4.png" width="530"/> 
</div>

基于FCN+FPN网络预测文本框，包含特征提取、特征合并、输出层三个阶段。

```python
def forward(self, x):
    C1, C2, C3, C4, C5 = self.backbone(x)
    up5 = self.deconv5(C5)
    ### deconv5 定义为ConvTranspose2d将c5通道数下降到和c4大小
    up5 = F.relu(up5)

    up4 = self.merge4(C4, up5)
    ### merge* 定义为Upsample，包括1x1,3x3卷积各一个，
    ### 和一个ConvTranspose2d将ci通道数下降到和c（i-1）一样大小
    up4 = F.relu(up4)

    up3 = self.merge3(C3, up4)
    up3 = F.relu(up3)

    up2 = self.merge2(C2, up3)
    up2 = F.relu(up2)

    up1 = self.merge1(C1, up2)
    output = self.predict(up1)
    ### predict 定义为Upsample，包括3x3和一个1x1
    ### 同时上采样到output_channel大小
    return output
```

### 2.3 推理阶段

前向网络生成TCL，TR和几何分数图。
对于TCL和TR，应用阈值Ttcl和Ttr。
TR和TCL的交集给出了TCL的最终预测值。利用不相交集（个人感觉就是连通域），有效地将TCL像素分成不同的文本实例。
设计一个跨步算法来提取指示文本实例的形状和矢量方向的有序点阵，并重建文本实例区域。同时应用两种简单的启发式算法来找出假阳性文本实例：

1）TCL像素的数量应至少为其平均半径的0.2倍；

 2）重建文本区域中至少一半的像素应归类为TR。

<div style="color:#0000FF" align="center">
<img src="demo\Fig5.png" width="530"/> 
</div>

跨步算法的基本步骤为：

step1：随机选取TCL中的一个点作为起始点，并将其居中（相对于文本域切面的居中）

step2：顺着TCL相反的方向反复进行Act（b）和Act（a）操作，直到分别达到俩端的终点为止。这样就会生成俩个有序点列表，其中每个点对于与当前TCL切面的中心位置

step3：连接俩个有序点列表即可得到中心轴列表。

step4：最终经过Act（c）将得到整个文本域mask。

<div style="color:#0000FF" align="center">
<img src="demo\Fig6.png" width="530"/> 
</div>

其中Act（a、b、c、d）分别进行的操作如下：

Act（a）：在TCL上给定一个点，我们可以画出切线和法线，分别表示为虚线和实线。 使用几何图可以轻松完成此步骤。 法线与TCL区域的交点的中点为中心点。

Act（b）：然后基于给定点，分别左右各取一定步长，步长的式子如下面所示，（注：如果根据步长计算[x,y]坐标出现越界，则缩小步长直到下一个点落在TCL内）
$$
( (1/2)r × cosθ; (1/2)r × sinθ) and (- (1/2)r × cosθ; - (1/2)r × sinθ)
$$
Act（c）：滑动该算法遍历中心轴并沿其绘制圆， 圆的半径从每个中心点对应的r映射获得。 圆圈所覆盖的区域表示预测的文本实例。

优点：

<font color="#dd0000">不仅可以检测文本，还可以预测它们的形状和轨迹。 此外，跨步算法可避免遍历所有相关像素，减少耗时。</font>

### 2.4 Label生成

<div style="color:#0000FF" align="center">
<img src="demo\Fig7.png" width="530"/> 
</div>

通过上述推理阶段生成分数图，假设检测文本对象为复杂的曲面多边形，他具备的基本特征有：

Ft1：文本实例是蛇形的，即它不会产生分叉； 

Ft2：文本实例具有两个边缘，分别是头部和尾部。 头部或尾部的两个边缘<font color="#dd0000">平行</font>但方向相反。

那么基本的Label制作步骤如下：

Stp1：**计算标注点之间的M距离**：

​	每2个相邻的点可以计算一个余弦距离M，计算公式如下，
$$
M(e_{i,i+1}) = cos(e_{i+1,i+2};e_{i-1,i})
$$
Stp2：**计算多边形的头尾端位置：**

​	M中的数值两两相乘，乘积最接近-1 的，是头尾两端。

Stp3：**计算骨架线的点向量**

​	该头尾分开的上下两端各取<font color="#dd0000">等量</font>的散点，并将上下的散点连接起来，取连接线的中心点作为骨架点，将所有的中点（点向量）连接起来，生成字体区域的骨架线。

Stp4：**生成Lable**

​	对骨架线的左右两端各缩小1/2rend的距离作为TCL，rend表示文本区域在头尾两个端点处的半径。因为单条线的敏感性太高，将生成的TCL扩大1/5个rend。

### 2.5 Loss计算

$$
L = L_{cls} + L_{reg}\\
L_{cls} = \lambda_1L_{tr} + \lambda_2L_{tcl}\\
L_{reg} = \lambda_3L_r + \lambda_4L_{sin} + \lambda_5L_{cos}
$$

Loss 主要分为**分类loss和回归loss**，分类TR和TCL为分类loss，半径角度这些为回归loss，TR和TCL使用的是交叉熵，并加入了**Oinline hard negative mining**去解决正负样本不平衡问题。

L_reg使用Smoothed loss计算，并且这些只对tcl内的计算，对tcl外的像素没有任何意义。

