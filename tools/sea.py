import cv2

# 全局变量
g_window_name = "Sea"  # 窗口名
g_window_wh = [1250, 695]  # 窗口宽高

g_location_win = [0, 0]  # 相对于大图，窗口在图片中的位置
location_win = [0, 0]  # 鼠标左键点击时，暂存g_location_win
g_location_click, g_location_release = [0, 0], [0, 0]  # 相对于窗口，鼠标左键点击和释放的位置

g_zoom, g_step = 1, 0.1  # 图片缩放比例和缩放系数
ori_map = cv2.imread("continent.png")  # 原始图片，建议大于窗口宽高（800*600）

sea_map = ori_map.copy()  # 缩放后的图片
mini_map = ori_map[g_location_win[1]:g_location_win[1] + g_window_wh[1], g_location_win[0]:g_location_win[0] + g_window_wh[0]]  # 实际显示的图片


# 矫正窗口在图片中的位置
# img_wh:图片的宽高, win_wh:窗口的宽高, win_xy:窗口在图片的位置
def check_location(img_wh, win_wh, win_xy):
    for i in range(2):
        if win_xy[i] < 0:
            win_xy[i] = 0
        elif win_xy[i] + win_wh[i] > img_wh[i] and img_wh[i] > win_wh[i]:
            win_xy[i] = img_wh[i] - win_wh[i]
        elif win_xy[i] + win_wh[i] > img_wh[i] and img_wh[i] < win_wh[i]:
            win_xy[i] = 0
    # print(img_wh, win_wh, win_xy)


# 计算缩放倍数
# flag：鼠标滚轮上移或下移的标识, step：缩放系数，滚轮每步缩放0.1, zoom：缩放倍数
def count_zoom(flag, step, zoom):
    if flag > 0:  # 滚轮上移
        zoom += step
        if zoom > 1 + step * 20:  # 最多只能放大到3倍
            zoom = 1 + step * 20
    else:  # 滚轮下移
        zoom -= step
        if zoom < step:  # 最多只能缩小到0.1倍
            zoom = step
    zoom = round(zoom, 2)  # 取2位有效数字
    return zoom


# OpenCV鼠标事件
def mouse(event, x, y, flags, param):
    global g_location_click, g_location_release, mini_map, sea_map, g_location_win, location_win, g_zoom
    sea = cv2.inRange(ori_map,
                      (cv2.getTrackbarPos('Rl', 'sea'), cv2.getTrackbarPos('Gl', 'sea'), cv2.getTrackbarPos('Bl', 'sea')),
                      (cv2.getTrackbarPos('Rh', 'sea'), cv2.getTrackbarPos('Gh', 'sea'), cv2.getTrackbarPos('Bh', 'sea')))
    if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
        g_location_click = [x, y]  # 左键点击时，鼠标相对于窗口的坐标
        location_win = [g_location_win[0], g_location_win[1]]  # 窗口相对于图片的坐标，不能写成location_win = g_location_win
    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):  # 按住左键拖曳
        g_location_release = [x, y]  # 左键拖曳时，鼠标相对于窗口的坐标
        h1, w1 = sea_map.shape[0:2]  # 缩放图片的宽高
        w2, h2 = g_window_wh  # 窗口的宽高
        show_wh = [0, 0]  # 实际显示图片的宽高
        if w1 < w2 and h1 < h2:  # 图片的宽高小于窗口宽高，无法移动
            show_wh = [w1, h1]
            g_location_win = [0, 0]
        elif w1 >= w2 and h1 < h2:  # 图片的宽度大于窗口的宽度，可左右移动
            show_wh = [w2, h1]
            g_location_win[0] = location_win[0] + g_location_click[0] - g_location_release[0]
        elif w1 < w2 and h1 >= h2:  # 图片的高度大于窗口的高度，可上下移动
            show_wh = [w1, h2]
            g_location_win[1] = location_win[1] + g_location_click[1] - g_location_release[1]
        else:  # 图片的宽高大于窗口宽高，可左右上下移动
            show_wh = [w2, h2]
            g_location_win[0] = location_win[0] + g_location_click[0] - g_location_release[0]
            g_location_win[1] = location_win[1] + g_location_click[1] - g_location_release[1]
        check_location([w1, h1], [w2, h2], g_location_win)  # 矫正窗口在图片中的位置
        mini_map = sea[g_location_win[1]:g_location_win[1] + show_wh[1], g_location_win[0]:g_location_win[0] + show_wh[0]]  # 实际显示的图片
    elif event == cv2.EVENT_MOUSEWHEEL:  # 滚轮
        z = g_zoom  # 缩放前的缩放倍数，用于计算缩放后窗口在图片中的位置
        g_zoom = count_zoom(flags, g_step, g_zoom)  # 计算缩放倍数
        w1, h1 = [int(ori_map.shape[1] * g_zoom), int(ori_map.shape[0] * g_zoom)]  # 缩放图片的宽高
        w2, h2 = g_window_wh  # 窗口的宽高
        sea_map = cv2.resize(sea, (w1, h1), interpolation=cv2.INTER_AREA)  # 图片缩放
        show_wh = [0, 0]  # 实际显示图片的宽高
        if w1 < w2 and h1 < h2:  # 缩放后，图片宽高小于窗口宽高
            show_wh = [w1, h1]
            cv2.resizeWindow(g_window_name, w1, h1)
        elif w1 >= w2 and h1 < h2:  # 缩放后，图片高度小于窗口高度
            show_wh = [w2, h1]
            cv2.resizeWindow(g_window_name, w2, h1)
        elif w1 < w2 and h1 >= h2:  # 缩放后，图片宽度小于窗口宽度
            show_wh = [w1, h2]
            cv2.resizeWindow(g_window_name, w1, h2)
        else:  # 缩放后，图片宽高大于窗口宽高
            show_wh = [w2, h2]
            cv2.resizeWindow(g_window_name, w2, h2)
        g_location_win = [int((g_location_win[0] + x) * g_zoom / z - x), int((g_location_win[1] + y) * g_zoom / z - y)]  # 缩放后，窗口在图片的位置
        check_location([w1, h1], [w2, h2], g_location_win)  # 矫正窗口在图片中的位置
        # print(g_location_win, show_wh)
        mini_map = sea_map[g_location_win[1]:g_location_win[1] + show_wh[1], g_location_win[0]:g_location_win[0] + show_wh[0]]  # 实际的显示图片
    cv2.imshow(g_window_name, mini_map)


def bars():
    def passing(x):
        pass
    cv2.namedWindow('sea')
    cv2.resizeWindow('sea', 1000, 618)
    cv2.createTrackbar('Rl', 'sea', 125, 255, passing)
    cv2.createTrackbar('Gl', 'sea', 125, 255, passing)
    cv2.createTrackbar('Bl', 'sea', 125, 255, passing)
    cv2.createTrackbar('Rh', 'sea', 127, 255, passing)
    cv2.createTrackbar('Gh', 'sea', 127, 255, passing)
    cv2.createTrackbar('Bh', 'sea', 127, 255, passing)


# 主函数
if __name__ == "__main__":
    bars()
    # 设置窗口
    cv2.namedWindow(g_window_name)
    # 设置窗口大小，只有当图片大于窗口时才能移动图片
    cv2.resizeWindow(g_window_name, g_window_wh[0], g_window_wh[1])
    cv2.moveWindow(g_window_name, 700, 100)  # 设置窗口在电脑屏幕中的位置
    # 鼠标事件的回调函数
    cv2.setMouseCallback(g_window_name, mouse)
    cv2.waitKey()  # 不可缺少，用于刷新图片，等待鼠标操作
    cv2.destroyAllWindows()