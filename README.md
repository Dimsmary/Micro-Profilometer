# Micro-Profilometer 微米级轮廓仪

## 项目简介

本项目主要设计了一个**亚微米级定位台**，通过与Micro-Epsilon共聚焦位移传感器进行结合后，设计成为微米级表面轮廓仪。
1、该轮廓仪能够完成对微小样品的表面轮廓测量（如晶圆裸片、金属表面等），分析其表面平整度或起伏结构。动态深度分辨率能够达到38nm，横纵分辨率能够达到8μm。
2、对于亚纳米级定位台，其分辨率能够达到200nm。基于该定位台，能够实现包括但不限于：扫描成像（如本项目所示的轮廓仪）、微流控操纵、光学对准等功能。

## 文件目录介绍

3DModel > 包含了项目所有的3D文件

3DModel > CNC > 包含了项目需要加工的CNC文件

3DModel > SolidWorks > 包含了项目的3D原始工程文件

ControlSoftware > 包含了项目使用到的脚本，请安装requirements.txt对应的pip包后运行gui.py以启动上位机

ControlSoftware > reverse.py 用于高度反转

Images > 包含压电滑台的性能数据

Pico2Firmware > 树莓派Pico2固件

ScanImages > 轮廓仪的扫描原始结果

PCB > 工程的PCB文件，请使用EasyEDA/立创EDA打开

## 复刻步骤

### PCB复刻

按照PCB文件夹下提供的文件进行复刻即可。有以下注意事项：

- 对于+5V LDO、DAC3、ADC区域电路为非必要部分，如无需求，可不进行焊接。
- 对于DAC部分的电路，如果DAC采用AD5761R，则ADR421可不进行焊接。如果采用AD5761，则需要进行焊接。对于本项目，默认采用AD5761R。AD5761R与AD5761在寄存器操作时略有不同，后续将进行介绍。

### 固件烧录

请使用VS Code打开Pico2Firmware>Table_Movement进行烧录，或使用Pico2Firmware目录下的.uf2文件完成烧录。

如果需要修改AD5761/AD5761R的初始化设置，请修改Table_Movement>lib>ad57x1>ad57x1.cpp中的\#define CONTROL_REG_BASE，该宏定义对AD5761/AD5761R的初始化进行了设置，包括内部参考电压源的开启/关闭，详情请参考对于数据手册的CONTROL REGISTER小节。

### 零件组装

所有需要加工的文件被放置在了3DModel > CNC下，请参考视频[链接待更新]或3DModel > SolidWorks下的XYTable.SLDASM以及full_assemble.SLDASM进行组装。

对于需要额外购买的Z轴定位台，其关键词为[Z轴升降台]，台面尺寸为60x60cm，行程为1cm。

对于fix.STEP，可以采用3D打印。