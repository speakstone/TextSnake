# 文本检测TextSnake

Author：Face++



## 0. 研究目的

1.基于轴对齐方式的矩形框，只对水平和竖直的文本奏效，对于倾斜，弯折，曲面的文本，会引入好多背景无关区域。

2.基于旋转的矩形框，也就是上一条的基础上加入了角度信息。可以适应于倾斜的文本，但是对于弯折，曲面的文本还是回引入背景无关区域。

3.基于凸四边形的方法，依然对曲面，弯折的文本无法适应。

## 1. 目标愿景

以解决水平、多方向和<font color="#dd0000">弯曲</font> 的文本检测。

## 2. 基本原理

<div style="color:#0000FF" align="center">
<img src="http://princepicbed.oss-cn-beijing.aliyuncs.com/blog_20181228172346.png" width="530"/> 
</div>