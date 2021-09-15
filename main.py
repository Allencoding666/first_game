# 遊戲執行的原理，就是進入一個迴圈，玩家輸入指令、滑鼠操作後，更新遊戲，然後在渲染到畫面上，之後再等玩家輸入指令，一直循環
# 遊戲迴圈 : 取得輸入 -> 更新遊戲 -> 畫面更新 -> 取得輸入...
# sprite類別，是pygame的內建類別，用來表示畫面上顯示的所有東西，有很多好用的函式，方便設定畫面上的東西要如何顯示、移動
import pygame
import random
import os
import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    password="allen7788",
    database="first_game",
)

cursor = connection.cursor()

FPS = 60

width = 500
height = 600

white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
yellow = (0, 255, 255)
black = (0, 0, 0)

# 遊戲初始化
pygame.init()

# 把音效模組初始化
pygame.mixer.init()

# 更改視窗標題
pygame.display.set_caption("Allen的太空生存戰")

# 創建視窗，參數要傳入一個元組，定義視窗的寬、高
screen = pygame.display.set_mode((width, height))

# 因為每台電腦效能不一樣，有的1秒可以執行迴圈1萬次，有的可以執行10萬次，這樣每個使用者的遊戲體驗會不一樣
# 可以使用pygame.time.Clock()對遊戲執行的時間做管理、操控
clock = pygame.time.Clock()

# 載入圖片，載入前要對pygame初始化(pygame.init())，不然會出錯
# 載入圖片，這邊使用pygame.image.load載入
# 因為每個人的電腦不同，圖片路徑使用os的函式，傳入目前這隻程式的路徑底下的"img"裡的"background.png"
# .convert()是將圖片轉成pygame較容易讀取的格式，這樣讀取速度比較快
background_img = pygame.image.load(os.path.join("img", "background.png")).convert()
player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
# 載入小的飛船圖片，當作剩餘的生命數
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(black)
# 設定視窗標題旁的小圖
pygame.display.set_icon(player_mini_img)
# rock_img = pygame.image.load(os.path.join("img", "rock.png")).convert()
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
# 載入多種石頭圖片，存到列表中
# 字串中不能使用變數，可以在字串外面加r，傳入的變數用{}，這樣就可以傳入變數了
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())

# 載入分數的字體，因為要將分數顯示在畫面上，而分數要有一個字體，所以要載入，這邊使用大部分系統都有的arial，但只有支援英文
# font_name = pygame.font.match_font("arial")
# 載入微軟正黑體
font_name = os.path.join("font.ttf")

# 建立一個函式，來處理把文字寫到畫面上的動作，我們規劃需要傳入五個參數，寫在甚麼平面上，甚麼文字，文字大小，xy座標

# 載入音樂
# 載入射擊的音效
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
# 載入飛船爆炸的音效
die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))

# 載入兩種不同的爆炸聲
expl_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav")),
]
# 載入背景音樂，這個比較不同，因為要一直循環播放
pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
# 調整背景音樂音量，參數傳入0~1
pygame.mixer.music.set_volume(0.3)

# 載入吃到寶藏的音效
gun_sound = pygame.mixer.Sound(os.path.join("sound", "奶酪.mp3"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))

# 載入爆炸圖片，這邊分成兩種，用大小來區分，子彈射到石頭為大爆炸，石頭撞到飛船為小爆炸，存放在字典內
# 加入飛船的爆炸
expl_anim = {}
# 大爆炸
expl_anim["lg"] = []
# 小爆炸
expl_anim["sm"] = []
# 飛船爆炸
expl_anim["player"] = []

# 載入爆炸圖片
for i in range(9):
    expl_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    # 將爆炸圖底圖的黑色改為透明
    expl_img.set_colorkey(black)
    # 把載入的圖片放入大爆炸圖內，且調整圖片大小
    expl_anim["lg"].append(pygame.transform.scale(expl_img, (75, 75)))
    # 把載入的圖片放入大爆炸圖內，且調整圖片大小
    expl_anim["sm"].append(pygame.transform.scale(expl_img, (30, 30)))

    player_expl_img = pygame.image.load(
        os.path.join("img", f"player_expl{i}.png")
    ).convert()
    # 將爆炸圖底圖的黑色改為透明
    player_expl_img.set_colorkey(black)
    # 把載入的圖片放入飛船爆炸圖內，因圖片大小剛好，就不調整圖片大小
    expl_anim["player"].append(player_expl_img)

# 載入寶藏圖
power_img = {}
power_img["shield"] = pygame.image.load(os.path.join("img", "shield.png")).convert()
power_img["gun"] = pygame.image.load(os.path.join("img", "gun.png")).convert()


def draw_text(surf, text, size, x, y):
    # 使用pygame函式創建一個文字的物件，需傳入兩個參數，一是字體，二是字體大小
    font = pygame.font.Font(font_name, size)
    # 把文字的物件render(渲染)出來，需傳入三個參數，一是要渲染的文字，二是一個布林值，True就是要用反鋸齒，三是字體顏色
    text_surface = font.render(text, True, white)
    # 把文字定位
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    # 把文字畫出來，需傳入兩個參數，一是要畫的東西，二是要畫的位置
    surf.blit(text_surface, text_rect)


# 產生石頭
def new_rock():
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock)


# 畫出血量
def draw_health(surf, hp, x, y):
    # 因為扣血可能扣超過，畫出來會怪怪的，先判斷血量有沒有小於0，如果小於，把他設定為0
    if hp < 0:
        hp = 0
    # 設定血量條的長高
    bar_length = 100
    bar_height = 10
    # 填滿血量，算出目前血量剩餘幾%，然後填滿多少%
    fill = (hp / 100) * bar_length
    # 設定血量的外框，用pygame內建函式，建立一個矩形，參數傳入x、y座標，矩形長、高
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    # 建立一個矩形，用來填滿血量長度
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    # 畫出血量
    pygame.draw.rect(surf, green, fill_rect)
    # 劃出血量的外框(要傳入第四個參數，設定外框線的粗細)
    pygame.draw.rect(surf, white, outline_rect, 2)


# 畫出生命數
def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        # 因為我們的小飛船寬為25，所以定位要間隔30再畫一個
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def draw_init():
    cursor.execute("SELECT `score` FROM `user_score` ORDER BY `score` DESC LIMIT 3;")
    recodes = cursor.fetchall()
    top_three_score = []
    for i in recodes:
        if i == None:
            top_three_score.append("0")
        else:
            top_three_score.append(str(i)[1:-2])

    screen.blit(background_img, (0, 0))
    draw_text(screen, "Allen的太空生存戰!", 48, width / 2, height / 4)
    draw_text(screen, "← →移動飛船，空白鍵發射子彈", 22, width / 2, height / 2)
    draw_text(screen, "按下任意鍵開始遊戲，Esc離開遊戲", 18, width / 2, height * 3 / 4)
    draw_text(screen, "排行榜", 16, 35, 5)
    draw_text(screen, "1. " + top_three_score[0], 16, 35, 25)
    draw_text(screen, "2. " + top_three_score[1], 16, 35, 45)
    draw_text(screen, "3. " + top_three_score[2], 16, 35, 65)

    pygame.display.update()
    # 等待鍵盤被玩家按
    waitting = True
    while waitting:
        # 設定程式執行的次數，每1秒最多執行幾次此迴圈
        clock.tick(FPS)
        # 取得輸入
        # pygame.event.get()會回傳一個列表(因為可能同時有很多動作)，儲存當下發生甚麼事件(按按鍵、滑鼠點擊...)
        for event in pygame.event.get():
            # 先判斷玩家是否點擊視窗的關閉或按下esc，是的話，直接結束遊戲
            if (
                event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                # 回傳True給close
                return True
            # 如果鍵盤被按下後鬆開
            elif event.type == pygame.KEYUP:
                waitting = False
                # 回傳False給close
                return False


def draw_final_score(final_score):
    screen.blit(background_img, (0, 0))
    draw_text(screen, "本次得分 : ", 48, width / 2, height / 3)
    draw_text(screen, str(final_score), 48, width / 2, height / 3 + 50)

    pygame.display.update()
    # 等待鍵盤被玩家按
    waitting = True
    while waitting:
        # 設定程式執行的次數，每1秒最多執行幾次此迴圈
        clock.tick(FPS)
        # 取得輸入
        # pygame.event.get()會回傳一個列表(因為可能同時有很多動作)，儲存當下發生甚麼事件(按按鍵、滑鼠點擊...)
        for event in pygame.event.get():
            # 先判斷玩家是否點擊視窗的關閉或按下esc，是的話，直接結束遊戲
            if (
                event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                # 回傳True給close
                return True
            # 如果鍵盤被按下後鬆開
            elif event.type == pygame.KEYUP:
                waitting = False
                # 回傳False給close
                return False


# 創建一個Player類別，繼承pygame裡內建的sprite類別
class Player(pygame.sprite.Sprite):
    def __init__(self):
        # call pygame裡內建的sprite類別的初始函式，初始函式要有兩個屬性image(表示要顯示的圖片)、rect(定位這張圖片)
        pygame.sprite.Sprite.__init__(self)
        # 使用pygame裡的圖片
        # self.image = pygame.Surface((50, 40))
        # 將該圖片填滿為綠色
        # self.image.fill(green)
        # 套用飛船的圖片，且使用pygame函式調整飛船大小
        self.image = pygame.transform.scale(player_img, (50, 30))
        # 將飛船黑色的底圖改為透明
        self.image.set_colorkey(black)
        # 將圖片框起，框起後才可以設定一些屬性
        self.rect = self.image.get_rect()
        # 使用圓形的碰撞判定，要加上radius的屬性，表示圓形的半徑，圖片寬度50，可用25慢慢試
        self.radius = 20
        # 這邊直接畫出圓形，只是用來測試圓形的大小有沒有合適
        # pygame.draw.circle(self.image, red, self.rect.center, self.radius)
        # 設定圖片的x,y座標
        self.rect.centerx = width / 2
        self.rect.bottom = height - 10
        # 設定一個控制數度的屬性(用於控制圖片的動速度)
        self.speedx = 8
        # 新增一個血量的屬性
        self.health = 100
        # 新增多條生命
        self.lives = 1
        # 判斷飛船是否隱藏中(這是用在剛復活的時候)
        self.hidden = False
        # 飛船隱藏時間
        self.hide_time = 0
        # 目前子彈等級
        self.gun = 1
        # 吃到升級子彈道具的時間
        self.gun_time = 0

    # 設定此物件的更新方式
    def update(self):
        # 取的現在時間
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now

        # 假如目前是隱藏狀態，且當update函式被呼叫的時間 - 隱藏時間 > 1000毫秒(1秒鐘)
        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = width / 2
            self.rect.bottom = height - 10
        # pygame會回傳一整串的布林值，來判斷鍵盤上每一個按鍵有沒有被按過，若有被按到回傳True，沒有則回傳False
        key_pressed = pygame.key.get_pressed()
        # 如果鍵盤方向鍵左鍵被按壓，回傳True，圖片座標x-2(畫面看起來圖片會像左移動)
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx
        # 如果鍵盤方向鍵右鍵被按壓，回傳True，圖片座標x-2(畫面看起來圖片會像右移動)
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx

        if self.rect.right > width:
            self.rect.right = width

        if self.rect.left < 0:
            self.rect.left = 0

        if self.lives == 0:
            self.kill()

    def shoot(self):
        # 如果沒有隱藏，才可以發射子彈
        if not (self.hidden):
            # 當子彈等級等於1
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                # 播放射擊音效
                shoot_sound.play()
            # 當子彈等級大於等於2
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                # 播放射擊音效
                shoot_sound.play()

    def hide(self):
        # 設定當前變為隱藏狀態
        self.hidden = True
        # 取得當前隱藏的時間點
        self.hide_time = pygame.time.get_ticks()
        # 把飛船定位在畫面之外，這樣玩家看飛船看起來就是隱藏了，用height + 500把飛船定位在畫面外面高度+500的地方
        self.rect.center = (width / 2, height + 500)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()


class Rock(pygame.sprite.Sprite):
    def __init__(self):
        # call pygame裡內建的sprite類別的初始函式，初始函式要有兩個屬性image(表示要顯示的圖片)、rect(定位這張圖片)
        pygame.sprite.Sprite.__init__(self)
        # 使用pygame裡的圖片
        # self.image = pygame.Surface((30, 40))
        # 將該圖片填滿為綠色
        # self.image.fill(red)
        # 套用石頭的圖片
        # self.image = rock_img
        # 將飛船黑色的底圖改為透明
        # self.image.set_colorkey(black)
        # 建立一個沒有旋轉過的圖片
        # self.image_ori = rock_img
        # 從一堆石頭中，隨機取出一種石頭
        self.image_ori = random.choice(rock_imgs)
        # 將飛船黑色的底圖改為透明
        self.image_ori.set_colorkey(black)
        # 複製沒有選轉過的圖片
        self.image = self.image_ori.copy()
        # 將圖片框起，框起後才可以設定一些屬性
        self.rect = self.image.get_rect()
        # 使用圓形的碰撞判定，要加上radius的屬性，表示圓形的半徑，圖片寬度width，可用一半慢慢試
        self.radius = self.rect.width * 0.85 / 2
        # 這邊直接畫出圓形，只是用來測試圓形的大小有沒有合適
        # pygame.draw.circle(self.image, red, self.rect.center, self.radius)
        # 設定圖片的x,y座標
        # 設定x座標在0~視窗寬度(width)，但是要扣掉物件本身的寬度，不然產生在視窗的width，這樣物件就會往右長出，導致看不到物件
        self.rect.x = random.randrange(0, width - self.rect.width)
        # 設定y座標在視窗上方(-100~-40)產生，這樣掉下來就會進到遊戲畫面中
        self.rect.y = random.randrange(-500, -400)
        # 設定一個控制數度的屬性(用於控制圖片的動速度)
        self.speedx = random.randrange(-3, 3)
        self.speedy = random.randrange(3, 10)
        # 設定原始的度數
        self.total_degree = 0
        # 設定轉動的度數，隨機設定轉動度數，順時針或逆時針轉
        self.rot_degree = random.randrange(-3, 3)

    # 圖片旋轉，使用pygame的內建函式讓圖片旋轉
    # 每轉動一次，圖片都會有一點點失真，我們設定FPS為60，這樣每秒鐘的失真會被疊加60次，不要讓圖片疊加就可以解決此問題
    # 將傳入的圖片改成沒有疊加過的圖片，就不會失真了
    def rotate(self):
        # 每次轉動度數加上去，第一次3度，第二次6度...，這樣圖片看起來才會真的在旋轉
        self.total_degree += self.rot_degree
        # 轉超過360度就轉一圈了，超過360度沒有意義，所以除以360取餘數
        self.total_degree = self.total_degree % 360
        # 圖片旋轉的函式，傳入(圖片, 選轉度數)
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        # 上面寫完執行時，石頭轉動會一直抖動，因為轉動時石頭的中心點一直改變，所以轉動起來會怪怪的
        # 解決方法是，當石頭每一次旋轉，就重新定位一次中心點
        # 先記住原本的中心的，存在center
        center = self.rect.center
        # 對轉動後得圖片重新定位
        self.rect = self.image.get_rect()
        # 設定轉動後圖片的中心點變為原本的中心點
        self.rect.center = center

    # 設定此物件的更新方式
    def update(self):
        # 讓石頭旋轉
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > height or self.rect.left > width or self.rect.right < 0:
            self.rect.x = random.randrange(0, width - self.rect.width)
            # 設定y座標在視窗上方(-100~-40)產生，這樣掉下來就會進到遊戲畫面中
            self.rect.y = random.randrange(-100, -40)
            # 設定一個控制數度的屬性(用於控制圖片的動速度)
            self.speedy = random.randrange(3, 10)
            self.speedx = random.randrange(-3, 3)


class Bullet(pygame.sprite.Sprite):
    # 這邊要傳入飛船的x, y座標，用於設定子彈的起始位置
    def __init__(self, x, y):
        # call pygame裡內建的sprite類別的初始函式，初始函式要有兩個屬性image(表示要顯示的圖片)、rect(定位這張圖片)
        pygame.sprite.Sprite.__init__(self)
        # 使用pygame裡的圖片
        # self.image = pygame.Surface((10, 20))
        # 將該圖片填滿為綠色
        # self.image.fill(yellow)
        # 套用子彈的圖片
        self.image = bullet_img
        # 將飛船黑色的底圖改為透明
        self.image.set_colorkey(black)
        # 將圖片框起，框起後才可以設定一些屬性
        self.rect = self.image.get_rect()
        # 設定圖片的x,y座標
        # 設定子彈的centerx等於飛船的
        self.rect.centerx = x
        # 設定y座標在視窗上方(-100~-40)產生，這樣掉下來就會進到遊戲畫面中
        self.rect.bottom = y
        # 設定一個控制數度的屬性(用於控制圖片的動速度)
        self.speedy = -10

    # 設定此物件的更新方式
    def update(self):
        self.rect.y += self.speedy
        # 判斷子彈是否超出視窗，超出的話就移除該子彈
        # kill()是sprite裡的函式，會去檢查所有sprite裡是否有子彈，有的話就會刪除子彈
        if self.rect.bottom < 0:
            self.kill()


class Explostion(pygame.sprite.Sprite):
    # 這邊要傳入爆炸的中心點(center)，還有現在要做的是大爆炸還是小爆炸(size)
    def __init__(self, center, size):
        # call pygame裡內建的sprite類別的初始函式，初始函式要有兩個屬性image(表示要顯示的圖片)、rect(定位這張圖片)
        pygame.sprite.Sprite.__init__(self)
        # 先把大小存起來
        self.size = size
        # 傳入爆炸的第一張圖，因為存在字典內，要先看要用大爆炸還是小爆
        self.image = expl_anim[self.size][0]
        # 將圖片框起，框起後才可以設定一些屬性
        self.rect = self.image.get_rect()
        # 設定中心點
        self.rect.center = center
        # 設定一個紀錄目前播放到第幾張爆炸圖
        self.frame = 0
        # 設定一個紀錄最後更新圖片的時間，此pygame函式會計算初始化到現在經過多少毫秒數
        self.last_update = pygame.time.get_ticks()
        # 設定經過幾毫秒才會更新到下一張圖片，因為我們設定FPS為60，這樣更新速度太快，會看不清楚
        self.frame_rate = 100

    # 設定此物件的更新方式
    def update(self):
        # 取得目前更新被執行的時間
        now = pygame.time.get_ticks()
        # 如果更新時間已超過50毫秒(根據我們的設定)
        if now - self.last_update >= self.frame_rate:
            # 把最後的更新時間改為現在時間
            self.last_update = now
            # 把目前撥放的爆炸圖變成下一張
            self.frame += 1
            # 如果目前的爆炸圖，已經播放到最後一張
            if self.frame == len(expl_anim[self.size]):
                # 刪除爆炸圖片
                self.kill()
            else:
                # 更新圖片到下一張爆炸圖，這邊size是看大爆炸還是小爆炸，frame是更新到第幾張圖片
                self.image = expl_anim[self.size][self.frame]
                # 記住當前的位置中心
                center = self.rect.center
                # 把爆炸圖重新定位
                self.rect = self.image.get_rect()
                # 把它定位在原本的中心點
                self.rect.center = center


class Power(pygame.sprite.Sprite):
    # 這邊要傳入道具的位置
    def __init__(self, center):
        # call pygame裡內建的sprite類別的初始函式，初始函式要有兩個屬性image(表示要顯示的圖片)、rect(定位這張圖片)
        pygame.sprite.Sprite.__init__(self)
        # 代表現在是哪一種道具，隨機出現
        self.type = random.choice(["shield", "gun"])
        self.image = power_img[self.type]
        # 將飛船黑色的底圖改為透明
        self.image.set_colorkey(black)
        # 將圖片框起，框起後才可以設定一些屬性
        self.rect = self.image.get_rect()
        # 設定道具位置
        self.rect.center = center
        # 設定道具移動速度
        self.speedy = 3

    # 設定此物件的更新方式
    def update(self):
        self.rect.y += self.speedy
        # 判斷道具是否超出視窗，超出的話就移除該道具
        # kill()是sprite裡的函式，會去檢查所有sprite裡是否有道具，有的話就會刪除道具
        if self.rect.top > height:
            self.kill()


# 創建一個sprite群組，裡面可以放很多sprite物件
all_sprites = pygame.sprite.Group()
rocks = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powers = pygame.sprite.Group()

player = Player()
all_sprites.add(player)
# 創建多個石頭
for i in range(8):
    new_rock()
# 起始遊戲分數
score = 0
# 播放背景音樂，參數傳入播放次數，無限次的話用-1
pygame.mixer.music.play(-1)

running = True

# 是否顯示初始頁面
show_init = True

# 遊戲迴圈
while running:
    if show_init:
        close = draw_init()
        # 判斷close，如果True，跳出迴圈，結束遊戲；如果False，繼續下面動作
        if close:
            break
        # 不顯示初始頁面，進入遊戲
        show_init = False
        # 創建一個sprite群組，裡面可以放很多sprite物件
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()

        player = Player()
        all_sprites.add(player)
        # 創建多個石頭
        for i in range(8):
            new_rock()
        # 起始遊戲分數
        score = 0

    # 設定程式執行的次數，每1秒最多執行幾次此迴圈
    clock.tick(FPS)
    # 取得輸入

    # pygame.event.get()會回傳一個列表(因為可能同時有很多動作)，儲存當下發生甚麼事件(按按鍵、滑鼠點擊...)
    for event in pygame.event.get():
        # 先判斷玩家是否點擊視窗的關閉或按下esc，是的話，running給Flase，跳出遊戲迴圈，執行迴圈外的pygame.quit()，結束遊戲
        if (
            event.type == pygame.QUIT
            or event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
        ):
            running = False
        # 如果鍵盤被按下
        elif event.type == pygame.KEYDOWN:
            # 如果鍵盤的空白鍵被按下
            if event.key == pygame.K_SPACE:
                # 射擊
                player.shoot()

    # 更新遊戲
    # 執行all_sprites裡，所有物件的update函式
    all_sprites.update()
    # 更新遊戲後，判斷傳入的群組是否有碰撞，如果有碰撞，是否刪除(True表示刪除，False表示不刪除)
    # 此碰撞函式會回傳一個字典，裡面是碰撞到的石頭跟子彈，key是石頭，value是子彈
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
    for hit in hits:
        # 隨機播放兩種石頭爆炸聲
        random.choice(expl_sounds).play()
        # 設定打到石頭獲得的分數，會因為是頭大小得到分數不一樣，用石頭的半徑來當分數
        # 因為rock函式中，radius在設定碰撞判定時，有*0.85，導致radius會有小數，這邊轉成int讓得分不要有小數位
        score += int(hit.radius)
        # 當石頭爆炸時，出現爆炸圖，這邊用大爆炸
        expl = Explostion(hit.rect.center, "lg")
        # 加到all_sprites，這樣才會畫出爆炸動畫
        all_sprites.add(expl)
        # 設定掉寶率
        # random.random()會產生一個0~1的數字，這邊設定掉寶率為9成
        if random.random() > 0.95:
            # 創建道具，道具出現的位置為石頭與子彈碰撞的位置
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            # 要看有沒有吃到道具，就判斷道具跟飛船是否碰撞
            powers.add(pow)
        # 建立新石頭
        new_rock()

    # 判斷石頭跟飛船是否發生碰撞，發生碰撞，則結束遊戲
    # 此碰撞函式會回傳一個列表
    # 傳入兩個群組和發生碰撞後，是否刪除群組，這邊發生碰撞後，就結束遊戲，所以有沒有刪除無所謂，就使用False
    # 若最後再加上pygame.sprite.collide_circle，可以改用圓形的碰撞判斷，會比原本矩形還精準
    # 使用圓形判斷方式，傳入的群組要有radius的屬性，指的是圓形的半徑
    # 後續加入飛船血量，所以將False改成True，因為石頭撞到飛船後，遊戲會繼續進行，所以要把石頭刪掉
    hits = pygame.sprite.spritecollide(
        player, rocks, True, pygame.sprite.collide_circle
    )
    # if hits:
    #     running = False
    # 因為hits會回傳一個列表，裡面放所有撞到飛船的石頭，本來是判斷有撞到就結束遊戲，現在改成血量，所以改用for來寫
    if player.health > 0:
        for hit in hits:
            # 當石頭爆炸時，出現爆炸圖，這邊用小爆炸
            expl = Explostion(hit.rect.center, "sm")
            # 加到all_sprites，這樣才會畫出爆炸動畫
            all_sprites.add(expl)
            # 因為石頭被刪除，所以要加回來，不然石頭會越來越少
            new_rock()
            # 用石頭的半徑當作扣除血量
            player.health -= hit.radius
            if player.health <= 0:
                # 播放飛船爆炸圖
                death_expl = Explostion(player.rect.center, "player")
                # 要加入到all_sprites才可以播放
                all_sprites.add(death_expl)
                # 播放飛船爆炸音效
                die_sound.play()
                player.lives -= 1
                if player.lives <= 0:
                    player.health = 0
                else:
                    # 把新的飛船生命調到100
                    player.health = 100
                    # 剛復活的時候有緩重時間，暫時隱藏飛船
                    player.hide()
                    # running = False

    # 判斷道具跟飛船是否碰撞
    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        if hit.type == "shield":
            shield_sound.play()
            player.health += 20
            if player.health >= 100:
                player.health = 100
        elif hit.type == "gun":
            gun_sound.play()
            player.gunup()

    if player.lives == 0 and not (death_expl.alive()):
        show_final_score = draw_final_score(score)
        cursor.execute("INSERT INTO `user_score`(`score`) VALUES(%d);" % score)
        connection.commit()
        if not show_final_score:
            show_init = True

    # 畫面顯示
    # 設定畫面顏色，參數為元組，分別為(R, G, B)顏色的比重，最高為255
    screen.fill(white)
    # 將背景圖畫上去，需傳入圖片，還有要放置的座標
    screen.blit(background_img, (0, 0))
    # 將all_sprites裡面的物件全部畫出來，畫在screen上
    all_sprites.draw(screen)
    # 畫出分數
    draw_text(screen, str(score), 18, width / 2, 10)
    # 畫出血量
    draw_health(screen, player.health, 5, 10)
    # 畫出生命數
    draw_lives(screen, player.lives, player_mini_img, width - 100, 15)
    # 用於更新畫面
    pygame.display.update()

pygame.quit()
cursor.close()
connection.close()
