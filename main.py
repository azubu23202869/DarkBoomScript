# coding: utf-8
# 包名:('com.komoe.darkboomgp')

import uiautomator2 as u2
import cv2
import time
import numpy as np

# In[6]:

threshold = 0.94    # 閥值
deviceVersion = 'img/'  # 圖片上層路徑

# In[7]:

c = u2.connect()    # adb連接裝置('127.0.0.1:5555)'
s = c.session()     # (填入包名)

# In[8]:

_ = c.screenshot('screen.png')  # 獲取初始裝置截圖

# In[9]:


# get some global properties
# 獲取全域的數據，包括裝置的長寬值，並輸出到終端上
globalScreen = cv2.imread("screen.png", 0)
screenWidth, screenHeight = globalScreen.shape[::-1]
print("ScreenWidth: {0}, ScreenHeight: {1}".format(screenWidth, screenHeight))


# In[10]:

# 通過opencv 去比對template是否有出現在img中，並返回匹配率
def getSimilarity(template, img, spec):
    _, _ = template.shape[::-1]
    # if spec is not None:
    #     print('check if is', spec.image_name)
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    #min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    #print("Max Value is {0}".format(max_val))
    #return max_val
    loc = np.where(res >= threshold)
    found = 0
    for pt in zip(*loc[::-1]):
        found = 1
    return found




# In[11]:


def takeScreenShot():
    c.screenshot('temp.png')
    img = cv2.imread('temp.png', 0)
    return img


# In[12]:


# get the location of template on image
def getButtonLocation(template, img):
    # c.screenshot('temp.png')
    # template = cv2.imread(buttonImageName,0)
    # img = cv2.imread('temp.png', 0)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    touch_loc = (max_loc[0] + w // 2, max_loc[1] + h // 2)
    return touch_loc, max_loc, w, h


# In[13]:


# touch the template on the image with offsets
def touchButton(template, img, xoffset=0, yoffset=0):
    touch_loc, _, _, _ = getButtonLocation(template, img)
    t_x, t_y = (touch_loc[0] + xoffset, touch_loc[1] + yoffset)
    print("Touching {0}, {1}".format(t_x, t_y))
    s.click(t_x, t_y)


# In[14]:


def recognizeAndProcessPage(specs):  # in the form of imageName => (template, action)

    img = takeScreenShot()
    print("===========================")
    # pick the highest applicable key
    # ss = max(specs, key=lambda s: get_similarity(s.imageTemplate, img, s))
    ss = None
    for spec in specs:
        match = getSimilarity(spec.imageTemplate, img, spec) == 1
        if match:
            ss = spec
            break
    if ss is None:
        print('unable recognize stage, wait for next time.')
        return

    # perform second filtering to filter by the actionButtonTemplate
    spec_name = ss.imageName
    filtered = [s for s in specs if s.imageName == ss.imageName]
    # print("= = = = = = = = = = = = = =")

    # ss = max(filtered, key=lambda s: get_similarity(s.actionTemplate, img, s))
    ss = None
    for spec in filtered:
        match = getSimilarity(spec.actionTemplate, img, spec) == 1
        if match:
            ss = spec
            break
    if ss is None:
        print('stage', spec_name, 'unable recognize action feature, program would not tap any position.')
    else:
        print("Picked : " + ss.imageName + " ==> " + ss.actionButtonName)
        ss.action(ss.actionTemplate, img)

    '''
    img = takeScreenShot()
    print("===========================")
    # pick the highest applicable key

    ss = max(specs, key=lambda s: getSimilarity(s.imageTemplate, img))

    # perform second filtering to filter by the actionButtonTemplate
    filtered = [s for s in specs if s.imageName == ss.imageName]
    print("= = = = = = = = = = = = = =")

    ss = max(filtered, key=lambda s: getSimilarity(s.actionTemplate, img))
    print("Picked : " + ss.imageName + " ==> " + ss.actionButtonName)
    ss.action(ss.actionTemplate, img)
    '''

# In[15]:


class Spec:
    # imageName : the image to scan to identify the scene
    # action : the action to execute upon match with imageName, receives (template, img), where
    #           template is the cv2 rep of the actionButtonName below, and the image is the
    #           current screen shot
    # actionButtonName: sometimes we want different button to be clicked while not checking this button
    #           the default value is the same as imageName
    def __init__(self, imageName, action, actionButtonName=None):
        if actionButtonName is None:
            actionButtonName = imageName
        self.imageName = imageName
        self.action = action  # action must receive (template, img) as the input variable
        self.actionButtonName = actionButtonName

        # load resources

        self.imageTemplate = cv2.imread(deviceVersion + imageName, 0)
        if self.imageTemplate is None:
            print("Error : ImageName is wrong")

        self.actionTemplate = cv2.imread(deviceVersion + actionButtonName, 0)
        if self.actionTemplate is None:
            print("Error : ActionButtonName is wrong")

        print("\nProcessing Spec: \nImageName: {0}\nActionButtonName : {1}".format(imageName, actionButtonName))
        # template1 = cv2.imread(imageName, 0)
        # template2 = cv2.imread(actionButtonName, 0)

def CheckRunState():
    pid = c.app_wait('com.komoe.darkboomgp', front=True, timeout=1)
    return pid


def LoginScreenSpec():
    def f(template, img):
        touchButton(template, img, 0, 45)
    return Spec("Server.PNG", f)


def LoginScreenGamePostClose():
    return Spec("Close.PNG", touchButton)


def SkipButton():
    return Spec("Skip.PNG", touchButton)



def GetItem():
    def f(template, img):
        touchButton(template, img, 0, 340)
    return Spec("GetItem.PNG", f)


def GoBattleButton():
    return Spec("GoBattle.PNG", touchButton)


def BattleList():
    return Spec("BattleList.PNG", touchButton)


def MainMission():
    return Spec("MainMission.PNG", touchButton)


def MainMission1():
    return Spec("MainMission1.PNG", touchButton)


def MainMission2():
    return Spec("MainMission2.PNG", touchButton)


def ConfirmFightButton():
    return Spec("ConfirmFightButton.PNG", touchButton)


def ConfirmButton():
    return Spec("ConfirmButton.PNG", touchButton)


def Battleing():
    def f(template, img):
        pass
    return Spec("Battleing.PNG", f)


def Battleing1():
    def f(template, img):
        pass
    return Spec("Battleing1.PNG", f)


def BackBattle():
    return Spec("BackBattle.PNG", touchButton)


def TouchContinue():
    return Spec("TouchContinue.PNG", touchButton)


def CheckHold():
    return Spec("CheckHold.PNG", touchButton)


def LevelUp():
    return Spec("LevelUp.PNG", touchButton)


def AttackButton():
    return Spec("AttackButton.PNG", touchButton)

def NoLocking():
    def f(template, img):
        touchButton(template, img, 0, 75)
    return Spec("NoLocking.PNG", f)


specs = [
    # 常規
    LoginScreenSpec,        # TapToStart
    LoginScreenGamePostClose,       # 登入介面關閉遊戲公告
    SkipButton,             # 點選跳過按鈕
    GetItem,                # 恭喜獲得點擊
    TouchContinue,          # 點擊繼續
    LevelUp,                # 指揮官等級提升
    Battleing,              # 戰鬥中(黑)
    Battleing1,             # 戰鬥中(白)
    BackBattle,             # 返回戰鬥
    NoLocking,              # 取得船艦點擊
    CheckHold,              # 確認港口佔領
    AttackButton,           # 戰力較高依然出擊
    # 戰鬥
    #GoBattleButton,         # 出征按鈕
    #BattleList,             # 右側三個點出現列表
    #MainMission,            # 列表選取主線戰鬥
    #MainMission1,           # 列表選取港口戰鬥
    #MainMission2,           # 列表選取港口戰鬥
    ConfirmFightButton,     # 確認出擊按鈕
    ConfirmButton,          # 確定按鈕
]
specs = [s() for s in specs]
while(True):
    try:
        if CheckRunState():
            recognizeAndProcessPage(specs)
            time.sleep(0.5)
        else:
            c.session('tw.wonderplanet.fantasticdays')
            time.sleep(2)
    except:
        time.sleep(2)


    #  def f(template, img):
    #      touchButton(template, img, -30, 30)