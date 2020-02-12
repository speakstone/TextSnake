

# 文本检测

Author：Face++



## 0. 研究目的

1.基于轴对齐方式的矩形框，只对水平和竖直的文本奏效，对于倾斜，弯折，曲面的文本，会引入好多背景无关区域。

2.基于旋转的矩形框，也就是上一条的基础上加入了角度信息。可以适应于倾斜的文本，但是对于弯折，曲面的文本还是回引入背景无关区域。

3.基于凸四边形的方法，依然对曲面，弯折的文本无法适应。

## 1. 目标愿景

以解决水平、多方向和<font color="#dd0000">弯曲</font> 的文本检测。

![](http://princepicbed.oss-cn-beijing.aliyuncs.com/blog_20181228172334.png)

## 2. 算法原理

### 2.1 基本思想

<div style="color:#0000FF" align="center">
<img src="http://princepicbed.oss-cn-beijing.aliyuncs.com/blog_20181228172346.png" width="630"/> 
</div>

利用多个可变的有序圆盘disk(<font color="#0000dd">蓝色</font>）按照中心线TCL（<font color="#00dd00">绿色</font>）方向滑动连接整个文本区域TR（<font color="#dddd00">黄色</font>），圆盘的几何形状与半径r和方位θ相关联。其与传统的表征方式(轴对齐矩形、旋转矩形和四边形)相比，不考虑文本区域的形状和长度。

### 2.2 网络结构

基于FCN+FPN网络预测文本框，包含特征提取、特征合并、输出层三个阶段。



