#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flatbuffers as Parser
import os
import string
import random
import shutil
import json
import argparse

import sys

sys_encoding = sys.getfilesystemencoding()

reload(sys)
sys.setdefaultencoding('utf8')

def encodeStr(msg):
    return msg.decode('utf-8').encode(sys_encoding)

def log(msg):
    print(encodeStr(msg))


ENGINE_VERSION = "3.10.0.0"

script_path = os.path.split(os.path.realpath(sys.argv[0]))[0]

with open(os.path.join(script_path, "header_rule.json"), "r") as fileObj:
    HeaderRules = json.load(fileObj)
    fileObj.close()

with open(os.path.join(script_path, "child_rule.json"), "r") as fileObj:
    ChildRules = json.load(fileObj)
    fileObj.close()

csdPath = ""


def writeFile(text):
    global csdPath

    with open(csdPath, "a") as fileObj:
        fileObj.write(text)
        fileObj.close()


def writeHeader(groupName):
    global ENGINE_VERSION, csdPath
    if os.path.exists(csdPath):
        os.remove(csdPath)
    randomId = random.sample(string.ascii_lowercase + "-" + string.digits, 36)
    randomId = "".join(randomId)
    text = ''
    text = text + '<GameFile>\n'
    text = text + '  <PropertyGroup Name="%s" Type="Layer" ID="%s" Version="%s" />\n' % (
        groupName, randomId, ENGINE_VERSION)
    text = text + '  <Content ctype="GameProjectContent">\n'
    text = text + '    <Content>\n'

    writeFile(text)


def writeFooter():
    text = ''
    text = text + '    </Content>\n'
    text = text + '  </Content>\n'
    text = text + '</GameFile>\n'
    writeFile(text)


def getImageOption(childKey, resourceData):
    fileType = "Default"
    if resourceData.ResourceType() == 0:
        fileType = "Normal"
    elif resourceData.ResourceType() == 1:
        fileType = "PlistSubImage"
    path = resourceData.Path()
    plistFile = resourceData.PlistFile()
    if path == "" and plistFile == "":
        return '  <%s />\n' % (childKey)
    text = '  <%s Type="%s" Path="%s" Plist="%s" />\n' % (
        childKey, fileType, path, plistFile)
    return text


def getEasingText(easingData):
    easingType = easingData.Type()
    if easingType == -1:
        return ""
    else:
        return '            <EasingData Type="%d" />\n' % (easingType)


def getFrameText(frameData, property):
    text = ""
    if property == "VisibleForFrame":
        realFrame = frameData.BoolFrame()
        text = text + '          <BoolFrame FrameIndex="%d" Tween="%s" Value="%s" />\n' % (
            realFrame.FrameIndex(), realFrame.Tween(), realFrame.Value())

    elif property == "Position":
        realFrame = frameData.PointFrame()
        text = text + '          <PointFrame FrameIndex="%d" X="%f" Y="%f">\n' % (
            realFrame.FrameIndex(), realFrame.Position().X(), realFrame.Position().Y())
        text = text + getEasingText(realFrame.EasingData())
        text = text + '          </PointFrame>\n'

    elif property == "Scale":
        realFrame = frameData.ScaleFrame()
        text = text + '          <ScaleFrame FrameIndex="%d" X="%f" Y="%f">\n' % (
            realFrame.FrameIndex(), realFrame.Scale().ScaleX(), realFrame.Scale().ScaleX())
        text = text + getEasingText(realFrame.EasingData())
        text = text + '          </ScaleFrame>\n'

    elif property == "RotationSkew":
        realFrame = frameData.ScaleFrame()
        text = text + '          <ScaleFrame FrameIndex="%d" X="%f" Y="%f">\n' % (
            realFrame.FrameIndex(), realFrame.Scale().ScaleX(), realFrame.Scale().ScaleX())
        text = text + getEasingText(realFrame.EasingData())
        text = text + '          </ScaleFrame>\n'

    elif property == "CColor":
        realFrame = frameData.ColorFrame()
        colorData = realFrame.Color()
        text = text + '          <ColorFrame FrameIndex="%d" Alpha="%d">\n' % (
            realFrame.FrameIndex(), colorData.A())
        text = text + '            <Color A="%d" R="%d" G="%d" B="%d" />' % (
            colorData.A(), colorData.R(), colorData.G(), colorData.B())
        text = text + '          </ColorFrame>\n'

    elif property == "FileData":
        realFrame = frameData.TextureFrame()
        text = text + '          <TextureFrame FrameIndex="%d" Tween="%s">\n' % (
            realFrame.FrameIndex(), realFrame.Tween())
        text = text + '          ' + \
            getImageOption("TextureFile", realFrame.TextureFile())
        text = text + '          </TextureFrame>\n'

    elif property == "FrameEvent":
        realFrame = frameData.EventFrame()
        text = text + '          <EventFrame FrameIndex="%d" Value="%d">\n' % (
            realFrame.FrameIndex(), realFrame.Value())
        text = text + '          </EventFrame>\n'

    elif property == "Alpha":
        realFrame = frameData.IntFrame()
        text = text + '          <IntFrame FrameIndex="%d" Value="%d">\n' % (
            realFrame.FrameIndex(), realFrame.Value())
        text = text + '          </IntFrame>\n'

    elif property == "AnchorPoint":
        realFrame = frameData.ScaleFrame()
        text = text + '          <ScaleFrame FrameIndex="%d" X="%f" Y="%f">\n' % (
            realFrame.FrameIndex(), realFrame.Scale().ScaleX(), realFrame.Scale().ScaleX())
        text = text + getEasingText(realFrame.EasingData())
        text = text + '          </ScaleFrame>\n'

    elif property == "ZOrder":
        realFrame = frameData.IntFrame()
        text = text + '          <IntFrame FrameIndex="%d" Value="%d">\n' % (
            realFrame.FrameIndex(), realFrame.Value())
        text = text + '          </IntFrame>\n'

    elif property == "ActionValue":
        realFrame = frameData.InnerActionFrame()
        # todo
    elif property == "BlendFunc":
        realFrame = frameData.BlendFrame()
        text = text + '          <BlendFuncFrame FrameIndex="%d" Src="%d" Dst="%d">\n' % (
            realFrame.FrameIndex(), realFrame.BlendFunc().Src(), realFrame.BlendFunc().Dst())
        text = text + '          </BlendFuncFrame>\n'
    return text


def getTimeline(timeLineData):
    property = timeLineData.Property()
    text = '        <Timeline ActionTag="%d" Property="%s">\n' % (
        timeLineData.ActionTag(), timeLineData.Property())
    frameNum = timeLineData.FramesLength()
    for i in range(frameNum):
        frameData = timeLineData.Frames(i)
        text = text + getFrameText(frameData, property)
    text = text + '        </Timeline>\n'
    return text


def writeAction(actionData):
    duration = actionData.Duration()
    speed = actionData.Speed()
    timelineNum = actionData.TimeLinesLength()
    text = '      <Animation Duration="%d" Speed="%f">\n' % (duration, speed)
    for i in range(timelineNum):
        timeLineData = actionData.TimeLines(i)
        text = text + getTimeline(timeLineData)

    text = text + '      </Animation>\n'
    writeFile(text)


def writeAnimation(parseData):
    animationNum = parseData.AnimationListLength()
    if animationNum == 0:
        return
    text = '      <AnimationList>\n'
    for i in range(animationNum):
        animationData = parseData.AnimationList(i)
        text = text + '        <AnimationInfo Name="%s" StartIndex="%d" EndIndex="%d" />\n' % (
            animationData.Name(), animationData.StartIndex(), animationData.EndIndex())
    text = '      </AnimationList>\n'
    writeFile(text)


def writeRootNode(nodeTree):
    widgetOption = nodeTree.Options().Data()
    widgetSize = widgetOption.Size()
    if not widgetSize:
        boneOption = Parser.BoneNodeOptions()
        boneOption._tab = widgetOption._tab
        widgetOption = boneOption.NodeOptions()

    widgetSize = widgetOption.Size()
    widgetName = widgetOption.Name()
    text = ''
    nodeObject = {
        "Node": "GameNodeObjectData",
        "Scene": "GameNodeObjectData",
        "Layer": "GameLayerObjectData",
        "Skeleton": "SkeletonNodeObjectData",
    }
    text = text + \
        '      <ObjectData Name="%s" ctype="%s">\n' % (
            widgetName, nodeObject[widgetName])
    text = text + \
        '        <Size X="%f" Y="%f" />\n' % (
            widgetSize.Width(), widgetSize.Height())
    writeFile(text)


def getRealOption(className, optionData):
    realOption = None
    optionClassName = className + "Options"
    try:
        optionClass = getattr(Parser, optionClassName)
    except Exception as e:
        print("error no match className: " + optionClassName)
        return

    if optionClass:
        realOption = optionClass()

    if realOption:
        realOption._tab = optionData.Data()._tab
        return realOption
    else:
        return optionData


def getHeaderOption(optionData, optionKey, valuePath, defaultValue="", replaceInfo=""):
    valueList = valuePath.split(".")
    parentValue = optionData
    for path in valueList:
        if not parentValue:
            return ""
        func = getattr(parentValue, path)
        if not func:
            return ""
        parentValue = func()
    result = str(parentValue)
    if result.upper() == str(defaultValue).upper():
        return ""
    result = result.replace("\n", "&#xA;")
    if result.find(".") != -1:
        result = result.rstrip("0")
        result = result.rstrip(".")

    renameDict = {}
    if replaceInfo != "":
        renameList = replaceInfo.split(",")
        for renameText in renameList:
            kvList = renameText.split("=")
            renameDict[kvList[0]] = kvList[1]
    if renameDict.has_key(result):
        result = renameDict[result]
    text = '%s="%s" ' % (optionKey, result)

    # scale9sprite special
    # if optionKey == "Scale9Enabled":
    # # if optionKey == "Scale9Enable" and result == "True":
    # 	text = text + getHeaderOption(optionData, "Scale9OriginX", "CapInsets.X")
    # 	text = text + getHeaderOption(optionData, "Scale9OriginY", "CapInsets.Y")
    # 	text = text + getHeaderOption(optionData, "Scale9Width", "CapInsets.Width")
    # 	text = text + getHeaderOption(optionData, "Scale9Height", "CapInsets.Height")
    return text


def getDefaultOptionHeader(widgetOption, tab):
    global HeaderRules
    text = tab + '<AbstractNodeData '
    DefaultRules = HeaderRules["Default"]
    for ruleOption in DefaultRules:
        text = text + getHeaderOption(widgetOption,
                                      ruleOption[0], ruleOption[1], ruleOption[2])
    return text


def writeOptionHeader(optionData, widgetOption, className, tab):
    global HeaderRules
    text = getDefaultOptionHeader(widgetOption, tab)
    if HeaderRules.has_key(className):
        ClassRules = HeaderRules[className]
        for ruleOption in ClassRules:
            text = text + \
                getHeaderOption(
                    optionData, ruleOption[0], ruleOption[1], ruleOption[2], ruleOption[3])
    text = text + 'ctype="%sObjectData">\n' % (className)
    writeFile(text)


def getChildProperty(optionData, optionKey, valuePath, renameProperty="", specialType=""):
    valueList = valuePath.split(".")
    parentValue = optionData
    for path in valueList:
        func = getattr(parentValue, path)
        if not func:
            return ""
        parentValue = func()

    if specialType == "ImageData":
        return getImageOption(optionKey, parentValue)

    funcList = dir(parentValue)
    validFuncList = []
    for funcName in funcList:
        if funcName.startswith("_"):
            continue
        if funcName == "Init" or funcName.startswith("GetRoot"):
            continue
        validFuncList.append(funcName)
    renameDict = {}
    if renameProperty != "":
        renameList = renameProperty.split(",")
        for renameText in renameList:
            kvList = renameText.split("=")
            renameDict[kvList[1]] = kvList[0]
    text = '  <%s ' % (optionKey)
    for funcName in validFuncList:
        func = getattr(parentValue, funcName)
        result = func()
        keyValue = funcName
        if renameDict.has_key(funcName):
            keyValue = renameDict[funcName]
        text = text + '%s="%s" ' % (keyValue, str(result))
    text = text + "/>\n"
    return text


def getDefaultOptionChild(widgetOption, tab):
    global ChildRules
    DefaultRules = ChildRules["Default"]
    text = ""
    for childRule in DefaultRules:
        text = text + tab + \
            getChildProperty(
                widgetOption, childRule[0], childRule[1], childRule[2], childRule[3])
    return text


def writeChildOption(realOption, widgetOption, className, tab):
    global ChildRules
    text = getDefaultOptionChild(widgetOption, tab)

    if ChildRules.has_key(className):
        ClassRules = ChildRules[className]
        for childRule in ClassRules:
            text = text + tab + \
                getChildProperty(
                    realOption, childRule[0], childRule[1], childRule[2], childRule[3])
    writeFile(text)


def writeOption(nodeTree, tab):
    optionData = nodeTree.Options()
    className = nodeTree.Classname()
    realOption = getRealOption(className, optionData)
    if not realOption:
        defaultText = tab + \
            '<AbstractNodeData ctype="%seObjectData">\n' % (className)
        writeFile(defaultText)
        return
    try:
        widgetOption = realOption.WidgetOptions()
    except:
        widgetOption = realOption.NodeOptions()

    writeOptionHeader(realOption, widgetOption, className, tab)
    writeChildOption(realOption, widgetOption, className, tab)


def recursionConvertTree(nodeTree, level=0):
    baseTab = '      ' + "    "*level
    if level > 0:
        writeOption(nodeTree, baseTab)

    childNum = nodeTree.ChildrenLength()
    if childNum > 0:
        writeFile(baseTab + '  <Children>\n')
        for i in range(childNum):
            child = nodeTree.Children(i)
            recursionConvertTree(child, level + 1)
        writeFile(baseTab + '  </Children>\n')
    if level > 0:
        writeFile(baseTab + '</AbstractNodeData>\n')
    else:
        writeFile(baseTab + '</ObjectData>\n')


def startConvert(csbPath, csparsebinary, targetDir):
    global csdPath

    _, fileName = os.path.split(csbPath)
    groupName, _ = os.path.splitext(fileName)
    csdPath = os.path.join(targetDir, groupName + ".csd")

    nodeTree = csparsebinary.NodeTree()

    writeHeader(groupName)
    writeAction(csparsebinary.Action())
    writeAnimation(csparsebinary)
    writeRootNode(nodeTree)
    recursionConvertTree(nodeTree)
    writeFooter()

def dealWithCsbFile(csbPath, fileDir):

    with open(csbPath, "rb") as fileObj:
        buf = fileObj.read()
        fileObj.close()

        buf = bytearray(buf)
        csparsebinary = Parser.CSParseBinary.GetRootAsCSParseBinary(buf, 0)
        startConvert(csbPath, csparsebinary, fileDir)

def parserArgs():

    parser = argparse.ArgumentParser(description=encodeStr('csb转化csd工具'))
    parser.add_argument('-s', '--source', action='store',help=encodeStr('csb文件导入路径'), type=str)
    parser.add_argument('-t', '--target', action='store',help=encodeStr('csd文件导出路径'), type=str)

    args = parser.parse_args()

    # args.source = 'C:/Users/Administrator/Desktop/csb2csd/test'
    # args.target = 'C:/Users/Administrator/Desktop/csb2csd/csb'
    if args.source and args.target:
		source = args.source
		target = args.target
    else:
		log("参数不完整！查看帮助")
		parser.print_help()
		return None, None
        
    return os.path.normpath(source), os.path.normpath(target)

def walkFileDir():

    source, target = parserArgs()
    if not (source and target):
        return None, None, None

    newDirs = [target]
    csbTypeFiles = {}
    elseTypeFiles = {}

    for root, dirs, files in os.walk(source):

        for name in dirs:

            newDirs.append(os.path.join(root, name).replace(source, target))

        for name in files:

            oldfileName = os.path.join(root, name)

            if os.path.splitext(name)[1] == '.csb':

                csbTypeFiles[oldfileName] = root.replace(source, target)
            else:
                elseTypeFiles[oldfileName] = oldfileName.replace(source, target)

    return newDirs, csbTypeFiles, elseTypeFiles

def makedirs(newDirs):

	if newDirs:
		log("创建目标目录")
		for dir in newDirs:
			# log(" 创建新目录:" + dir)
			if not os.path.exists(dir):
				os.mkdir(dir)

def parserFiles(csbTypeFiles):

	if csbTypeFiles:

		log("解析csb文件生成csd文件到相应目录")
		i = 1
		count = len(csbTypeFiles.items())
		for key, values in csbTypeFiles.items():
			log(" 解析csb文件(%d/%d): %s"%( i, count, key))
			
			dealWithCsbFile(key, values)
			i += 1

def copyFiles(elseTypeFiles):

	if elseTypeFiles:
		
		log("复制其他类型文件到相应目录")
		
		i = 1
		count = len(elseTypeFiles.items())
		for key, values in elseTypeFiles.items():
			log(" 复制其他文件(%d/%d): %s 到 %s"%( i, count, key, values))
			shutil.copy(key, values)
			i += 1

def main():

    newDirs, csbTypeFiles, elseTypeFiles = walkFileDir()
    
    makedirs(newDirs)
    parserFiles(csbTypeFiles)
    copyFiles(elseTypeFiles)
    
if __name__ == '__main__':
    main()
