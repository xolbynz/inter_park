from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import random
import pytesseract
import time
import re
import os
import glob
from datetime import datetime
import cv2 
import numpy as np
import time
from datetime import datetime
import pytesseract
import threading
wait_sec = 10
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

puzzle_path="oasis.jpg"
# 예매할 자리 수 (최대 2매)
wanted_seats_count = 1


# 인터파크 아이디 생년월일
birth_date = input("인터파크 주민번호 앞에: ") 
# your_username=input("인터파크 아이디 틀리지마: ") 
# your_password=input("인터파크 비밀번호 틀리지마: ") 
# 결제할 카카오톡 정보
# 핸드폰 번호
kakao_phone_number = input("까까오페이 핸드폰번호: ") 
# 생년월일
kakao_birth_date = input("까까오페이 주민번호 앞에: ") 

options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

print("✅ 기존 Chrome 세션 연결 완료")


def chapcha():    
    try:
        while True:
            WebDriverWait(driver, 0.2).until(EC.presence_of_element_located((By.ID, "imgCaptcha")))
            capcha_layer = driver.find_element(By.ID, 'imgCaptcha')
            if capcha_layer.is_displayed():
                try:
                    byte_data=capcha_layer.screenshot_as_png
                    np_data = np.frombuffer(byte_data, dtype=np.uint8)
                    image = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 91, 1)
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=1)

                    cnts = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
                    for c in cnts:
                        area = cv2.contourArea(c)
                        if area < 50:
                            cv2.drawContours(image, [c], -1, (0, 0, 0), -1)
                    kernel2 = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
                    image = cv2.filter2D(image, -1, kernel2)
                    result = 255 - image
                    captcha_text = pytesseract.image_to_string(result)
                    driver.switch_to.default_content()
                    driver.switch_to.frame(iframe_seat)
                    # 'validationTxt' 클래스를 가진 요소를 찾습니다
                    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.CLASS_NAME, "validationTxt")))
                    validation_txt_element = driver.find_element(By.CLASS_NAME, "validationTxt")
                    if captcha_text[-1]=='\n':
                        captcha_text=captcha_text[:-1]
                    if len(captcha_text)!=6:
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.CLASS_NAME, "refreshBtn")))
                        element = driver.find_element(By.CLASS_NAME, "refreshBtn")
                        element.click()
                        time.sleep(1)
                        continue
                    else:
                        # 요소에 클릭을 수행합니다.
                        validation_txt_element.click()
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "txtCaptcha")))
                        captcha_input = driver.find_element(By.ID, "txtCaptcha")
                        captcha_input.send_keys(captcha_text)
                        print(captcha_text)
                        # element_to_click = driver.find_element(By.XPATH, "//*[@id='divRecaptcha']/div[1]/div[4]/a[2]")
                        element_to_click = driver.find_element(By.XPATH, "//a[@onclick='fnCheck()']")

                        # 요소 클릭
                        element_to_click.click()
                        time.sleep(1)
                    
                        if capcha_layer.is_displayed() == 0:
                            # print('클리어')
                            break
                        else:
                            WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.CLASS_NAME, "refreshBtn")))
                            element = driver.find_element(By.CLASS_NAME, "refreshBtn")
                            element.click()
                            continue
                except Exception as e :
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.CLASS_NAME, "refreshBtn")))
                        element = driver.find_element(By.CLASS_NAME, "refreshBtn")
                        element.click()
                        continue                        
            else:
               break 
    except TimeoutException:
        pass



def puzzle():
    
    try:
        while True:
            WebDriverWait(driver,0.2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "canvas")))
            canvas_element = driver.find_element(By.CSS_SELECTOR, 'canvas')
            if canvas_element.is_displayed():
                try:
                    img_data = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas_element)
                    og_image=cv2.imread(puzzle_path)
                    # resized_image = cv2.resize(og_image, (capch_image_w, capch_image_h))
                    import base64
                    from PIL import Image
                    from io import BytesIO 
                    img = Image.open(BytesIO(base64.b64decode(img_data)))
                    capcha_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    og_image_resized = cv2.resize(og_image, (capcha_img.shape[1], capcha_img.shape[0]))
                    # 그레이스케일로 변환
                    original_gray = cv2.cvtColor(og_image_resized, cv2.COLOR_BGR2GRAY)
                    blurred_gray = cv2.cvtColor(capcha_img, cv2.COLOR_BGR2GRAY)

                    # 이미지 간 차이 계산
                    diff = cv2.absdiff(original_gray, blurred_gray)
                    _, thresh = cv2.threshold(diff, 100, 255, cv2.THRESH_BINARY)

                    # 차이가 있는 영역의 좌표 찾기
                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    min_x, min_y = capcha_img.shape[1], capcha_img.shape[0] # 초기 최소값 설정
                    max_x, max_y = 0 , 0
                    for contour in contours:
                        x, y, w, h = cv2.boundingRect(contour)
                        # x_min, y_min 좌표 출력
                        if w>20 and h>20:
                        # 최소 x, y 좌표 업데이트
                            if x < min_x:
                                min_x = x
                            if y < min_y:
                                min_y = y
                            if x > max_x:
                                max_x=x 
                            if y > max_y:
                                max_y= y 
                        # 가장 작은 x_min, y_min 좌표 출력
                            # print("x_min:", x, "y_min:", y,"w",w,"h",h)
                            # 선택적: 차이 영역 시각화
                            cv2.rectangle(og_image_resized, (x, y), (x + w, y + h), (0, 255, 0), -1)
                    # cv2.imwrite('Difference.jpg', og_image_resized)
                    # print("가장 작은 x_min:", min_x, "가장 작은 y_min:", min_y)
                
                    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.XPATH, '//*[@id="captchSlider"]/div/div[2]/div')))
                    slider_btn = driver.find_element(By.XPATH, '//*[@id="captchSlider"]/div/div[2]/div')
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)

                    # 슬라이더 버튼을 드래그하는 동작을 수행합니다.
                    # 예를 들어, 오른쪽으로 100 픽셀 이동한다고 가정합니다.
                    offset = max_x+14.3  # 원하는 만큼의 픽셀값으로 변경
                    #################################################################################여기는 계속 디버그로 수정
                    steps = 10
                    actions.click_and_hold(slider_btn)
                    # actions.click_and_hold(slider_btn).move_by_offset(offset, 0).release().perform()
               
                    for _ in range(steps):
                        actions.move_by_offset(int(offset / steps), random.uniform(-3, 3)).perform()
                        actions = ActionChains(driver)  # ActionChains 재설정

                    # 마우스 버튼을 놓습니다.
                    actions.release().perform()
                    time.sleep(1)
                    if not canvas_element.is_displayed():
                        break
                    else:
                        continue
                except Exception as e :
                    continue
            else:
                break
            
    except TimeoutException:
        pass
def alert_check():
    global driver
    # 경고창이 있는지 확인
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text  # 경고창의 내용을 가져옴
        print("경고창 내용:", alert_text)
        alert.accept()  # "확인" 버튼 클릭        
        # 경고창이 존재하면 True 반환
        is_alert_present = True
    except NoAlertPresentException:
        # 경고창이 존재하지 않으면 False 반환
        is_alert_present = False
    
    return is_alert_present  

def book_Delivery_check():
    global driver
    formBook = driver.find_elements(By.XPATH, "//form[@name='formBook']")
    if formBook:
        formBook[0].get_attribute("action")
        action_value = formBook[0].get_attribute("action")

        if action_value:
            # action 값에 따라 다른 조치를 취할 수 있습니다.
            if "/Book/BookPrice.asp" in action_value:
                # /Book/BookPrice.asp에 대한 처리
                return False
            elif "/Book/BookDelivery.asp" in action_value:
                # BookDelivery.asp에 대한 처리   
                return True 
            else:
                return False
        else:
            return False
    else:
        return False

# 로그인 페이지 열기
# driver.get('https://tickets.interpark.com/goods/24013437?GoodsCode=24013437')
# driver.get('https://tickets.interpark.com/goods/24017510')
# https://tickets.interpark.com/goods/24017510
# 사용자가 직접 로그인
# input("로그인 한 후에는 'y'를 입력하고 Enter 누르세요.")

# # # driver.get('https://tickets.interpark.com/goods/23016975') #황영웅
# driver.get('https://tickets.interpark.com/goods/24016943?GoodsCode=24016943') #cp

# input("준비 되면 'y'를 입력하고 Enter 누르세요.")

# try:
#     # 팝업이 표시될 때까지 기다림
#     popup_body = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "popupBody"))
#     )
#     print("팝업이 나타났습니다.")

#     # "하루동안 보지 않기" 링크 클릭
#     dont_show_checkbox = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.CLASS_NAME, "popupCheckLabel"))
#     )
#     dont_show_checkbox.click()
#     print("하루동안 보지 않기 클릭 성공")
# except Exception as e:
#     print(f"팝업 처리 중 오류 발생: {e}")
# try:
#     # 버튼 찾기 (클래스를 기반으로 요소 찾기)
#     button = driver.find_element(By.CSS_SELECTOR, 'a.sideBtn.is-primary[data-check="false"]')

#     # 마우스 이동 및 클릭 (자연스럽게 보이기 위해 사용)
#     actions = ActionChains(driver)
#     actions.move_to_element(button).pause(1).click().perform()
    
#     print("버튼 클릭 성공!")
# except Exception as e:
#     print("버튼 클릭 실패:", e)

# time.sleep(5)

############################
print("여기서 로그인 한번만 하자~~~ 브레이크 걸어")
    # 3. 아이디 입력
# time.sleep(5)
# username_input = driver.find_element(By.NAME, "username")  # "username"은 input의 name 속성
# username_input.send_keys(your_username)  # 여기에 실제 아이디 입력
# time.sleep(1)
# # 4. 비밀번호 입력
# password_input = driver.find_element(By.NAME, "password")  # "password"는 input의 name 속성
# password_input.send_keys(your_password)  # 여기에 실제 비밀번호 입력
# time.sleep(1)
# # 5. 로그인 버튼 클릭
# login_button = driver.find_element(By.CLASS_NAME, "button_btnStyle__SEYzh")
# login_button.click()

# 6. 로그인 후 대기 (필요 시)
# time.sleep(5)
####################################
try:
    # 버튼 찾기 (클래스를 기반으로 요소 찾기)
    button = driver.find_element(By.CSS_SELECTOR, 'a.sideBtn.is-primary[data-check="false"]')

    # 마우스 이동 및 클릭 (자연스럽게 보이기 위해 사용)
    actions = ActionChains(driver)
    actions.move_to_element(button).pause(1).click().perform()
    
    print("버튼 클릭 성공!")
except Exception as e:
    print("버튼 클릭 실패:", e)

## 좌석 선택 창
# 새 창 전환하기
# 새 창이나 탭이 열릴 때까지 기다림
time.sleep(5)
WebDriverWait(driver, 30).until(lambda d: len(d.window_handles) > 1)
window_handles = driver.window_handles
driver.switch_to.window(window_handles[1])


datelist=['20251021']
# datelist=['20250125','20250126']
# find_seat = False
capcha_check=True
while True:
    try:
        # driver.delete_all_cookies()
        # data_str=datelist[int(round(random.uniform(0, 1)))]
        data_str=datelist[0]
        # iframe으로 전환
        # 나올 때까지 기다리기
        # # 새 창이나 탭의 로딩을 기다림
        # driver.maximize_window()
        print("set window")
        driver.set_window_size(1000, 800) 
        # driver.set_window_position(-2000, 0)  # 화면 왼쪽 바깥으로 이동
        # WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        WebDriverWait(driver, 1000).until(EC.presence_of_element_located((By.ID, "ifrmSeat")))
        iframe_seat = driver.find_element(By.ID, "ifrmSeat")
        driver.switch_to.frame(iframe_seat)
        print("iframe_seat switch")
    #     # 보안문자 넘어가기
    #     # display: none; 검사
        
        chapcha()
        puzzle()

        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "PlayDate")))
        # driver.execute_script("document.getElementById('PlayDate').value = '20231231';")
        # driver.execute_script("document.getElementById('PlayDate').value = "+data_str+";")
        # time.sleep(1)
        # driver.execute_script("document.getElementById('PlaySeq').value = '000';") 
        # driver.execute_script("document.getElementById('PlaySeq').value = '001';")
        element = driver.find_element(By.ID, "PlayDate")
        select_element = Select(element)

        select_element.select_by_value(data_str)   # "19시 30분"의 value 값을 지정하세요.
        time.sleep(0.1)
        element = driver.find_element(By.ID, "PlaySeq")

        # Select 요소로 변환
        select_element = Select(element)

        # # "19시 30분" 선택
        # if data_str==datelist[1]:
        #     select_element.select_by_value("002")  # "19시 30분"의 value 값을 지정하세요.
        # else :
        #     # select_element.select_by_value("001")  
        #     select_element.select_by_value("003")  
        select_element.select_by_value("001")  
        WebDriverWait(driver, 80).until(
            EC.presence_of_all_elements_located((By.XPATH, "//tr[@id='GradeRow']/td/div/span[@class='select']"))
        )
   
        # 요소들이 로드되었으므로 이제 찾을 수 있습니다.
        seat_grades = driver.find_elements(By.XPATH, "//tr[@id='GradeRow']/td/div/span[@class='select']")
        is_have_seat=False
        for seat_grade in seat_grades:
            text = seat_grade.text
            if  True:
            # if  "스탠딩" in text:
            # if text == "지정석":
                actions = ActionChains(driver)
                actions.move_to_element(seat_grade).perform()
                # "스탠딩석" 요소 클릭
                time.sleep(0.1)  # 자바스크립트로 DOM 변경 시작할 시간을 줌
                seat_grade.click()
                grade_detail = driver.find_element(By.ID, "GradeDetail")
                style = grade_detail.get_attribute("style")
                print(f"클릭한 요소: {seat_grade.text} ,{style}")
                time.sleep(0.1)
                # is_have_seat = True
                # 스탠딩석 클릭 후 링크들 로드 대기
                # 스탠딩석 클릭 후 상세 링크들이 모두 로드될 때까지 기다리기
                # wait = WebDriverWait(driver, 1)
                # wait.until(EC.visibility_of_element_located((By.XPATH, "//td[@id='GradeDetail']//ul/li/a")))
                # wait.until(EC.element_to_be_clickable((By.XPATH, "//td[@id='GradeDetail']//ul/li/a")))
                # links = driver.find_elements(By.XPATH, "//td[@id='GradeDetail']//ul/li/a")

                xpath = "//td[@id='GradeDetail' and not(contains(@style, 'display: none'))]//ul/li/a"
                wait = WebDriverWait(driver, 10)

                # 요소가 화면에 보일 때까지 대기
                wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
                # 요소가 클릭 가능할 때까지 대기
                wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

                # 이후 보이는 GradeDetail 블록 내의 모든 a 태그 수집
                links = driver.find_elements(By.XPATH, xpath)
                ######################################### 여기가 조건 주는거야
                print("여기가 조건 주는거야 50만원짜리는 빡셈")
                #######################################
                for link in links:
                    if  int(link.text[:3]) in [1,4] :
                        continue
                    print(f"클릭할 링크: {link.text}")

                    driver.execute_script("arguments[0].click();", link)  # JavaScript로 클릭
                    time.sleep(0.1)  # 각 클릭 간에 대기 시간 추가 (필요 시 조정)
                    # `ifrmSeatDetail`로 전환
                    iframe = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ifrmSeatDetail"))
                    )
                    driver.switch_to.frame(iframe)

                    # `divSeatBox` 내의 `SeatR` 클래스 요소들 찾기
                    # `divSeatBox` 내 모든 SeatN 요소 찾기
                    seat_found=False
                    try:
                        # SeatN 요소가 있는지 확인
                        seat_n_element = WebDriverWait(driver, 0.2).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#divSeatBox .SeatN"))
                        )

                        # SeatN 요소가 있으면 클릭
                        title = seat_n_element.get_attribute("title")
                        print(f"예약 가능 좌석 발견: {title}")
                        seat_n_element.click()  # 좌석 클릭
                        print("좌석 클릭 성공")
                        seat_found=True
                        # 부모 프레임으로 전환 후 확인 버튼 클릭
                        driver.switch_to.parent_frame()
                        confirm_button = WebDriverWait(driver, 1).until(
                            EC.element_to_be_clickable((By.ID, "NextStepImage"))
                        )
                        confirm_button.click()
                        print("좌석선택완료 버튼 클릭 성공")

                    except TimeoutException:
                        print("SeatN 요소를 찾을 수 없습니다. 빈 좌석이 없거나 예약 가능한 좌석이 없습니다.")
                    except Exception as e:
                        print(f"오류 발생: {e}")
                    # #######################################################
                    # seat_elements = WebDriverWait(driver, 10).until(
                    #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#divSeatBox span"))
                    # )
                    # seat_found=False
                    # # SeatR과 SeatN 구분
                    # for index, seat in enumerate(seat_elements, start=1):
                    #     class_name = seat.get_attribute("class")
                    #     if "SeatR" in class_name:
                    #         print(f"Seat {index}: SeatR - 빈 좌석")
                    #     elif "SeatN" in class_name:
                    #         title = seat.get_attribute("title")  # title 속성 확인
                    #         print(f"Seat {index}: SeatN - 예약 가능 좌석, 정보: {title}")
                    #         try:
                    #             seat.click()  # 좌석 클릭
                    #             print(f"SeatN {index} 클릭 성공")
                    #             # 좌석선택완료 버튼 클릭
                    #             driver.switch_to.parent_frame()
                    #             confirm_button = WebDriverWait(driver, 10).until(
                    #                 EC.element_to_be_clickable((By.ID, "NextStepImage"))
                    #             )
                    #             confirm_button.click()
                    #             print("좌석선택완료 버튼 클릭 성공")
                    #             seat_found = True  # 좌석을 찾았으므로 루프 종료
                    #             break
                    #         except Exception as e:
                    #             print(f"좌석 클릭 또는 버튼 클릭 실패: {e}")
                    #     else:
                    #         print(f"Seat {index}: 알 수 없는 클래스 - {class_name}")
                    # #############################################################################
                    if not seat_found:
                        print("SeatN 요소가 없습니다. 다시 시도합니다.")
                        # driver.refresh()
                        driver.switch_to.parent_frame()
                        # time.sleep(2)
                        continue  # 다시 루프를 돌림
                    else:
                        print("넘어감~~")
                        driver.switch_to.default_content()
                        # iframe으로 전환
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "ifrmBookStep")))
                        iframe_bookstep = driver.find_element(By.ID, "ifrmBookStep")
                        driver.switch_to.frame(iframe_bookstep)

                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                        # <select> 요소 찾기
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.NAME, "SeatCount")))
                        select_element = driver.find_element(By.NAME, "SeatCount")

                        # Select 객체 생성
                        select_object = Select(select_element)

                        # "2매" 선택 (옵션 값 "2" 사용)
                        select_object.select_by_value(f"{wanted_seats_count}")

                        # iframe_bookstep 작업 완료 후, 메인 페이지로 다시 전환
                        driver.switch_to.default_content()

                        # 다음 버튼 클릭
                        # 'SmallNextBtnLink' ID를 가진 <a> 요소 찾기 (다음 버튼)
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "SmallNextBtnImage")))
                        # next_button = driver.find_element(By.XPATH, "//img[@src='//ticketimage.interpark.com/TicketImage/onestop/btn_next_02_on.gif']")
                        next_button = driver.find_element(By.ID, "SmallNextBtnImage")
                        next_button.click()
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "ifrmBookStep")))
                        iframe_bookstep = driver.find_element(By.ID, "ifrmBookStep")
                        driver.switch_to.frame(iframe_bookstep)

                    #     # 'YYMMDD' ID를 가진 <input> 요소 찾기
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "YYMMDD")))
                        input_element = driver.find_element(By.ID, "YYMMDD")

                        # 숫자 입력
                        input_element.send_keys(birth_date)    

                        # iframe 나오기
                        driver.switch_to.default_content()

                        # 다음 버튼 누르기
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "SmallNextBtnImage")))
                        next_button = driver.find_element(By.ID, "SmallNextBtnImage")
                        next_button.click()


                        ## 결제 선택
                        print("카카오페이 선택")
                        # iframe으로 전환
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "ifrmBookStep")))
                        iframe_bookstep = driver.find_element(By.ID, "ifrmBookStep")
                        driver.switch_to.frame(iframe_bookstep)

                        # "카카오" 라벨을 가진 라디오 버튼 찾기
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(), '카카오')]/preceding-sibling::input[@type='radio']")))
                        bank_transfer_radio = driver.find_element(By.XPATH, "//label[contains(text(), '카카오')]/preceding-sibling::input[@type='radio']")

                        # 라디오 버튼 클릭
                        bank_transfer_radio.click()  
                        # 현금영수증 체크박스를 찾고 상태 확인
                        try:
                            # '현금영수증 신청' 체크박스 요소 가져오기
                            cash_receipt_checkbox = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.ID, "CashReceiptCheck"))
                            )

                            # 체크 상태 확인
                            is_checked = cash_receipt_checkbox.is_selected()
                            print(f"현금영수증 신청 체크 상태: {'체크됨' if is_checked else '체크 안됨'}")

                            # 체크되어 있으면 해제
                            if is_checked:
                                cash_receipt_checkbox.click()
                                print("현금영수증 신청 체크 해제 완료")
                            else:
                                print("현금영수증 신청이 이미 체크 해제 상태임")
                        except Exception as e:
                            print(f"체크박스 처리 중 오류 발생: {e}")

                    #     # iframe 나오기
                        driver.switch_to.default_content()
                        
                    #     # 다음 버튼 누르기
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "SmallNextBtnImage")))
                        next_button = driver.find_element(By.ID, "SmallNextBtnImage")
                        next_button.click()    


                    #     ## 결제하기
                        print("결제하기")
                        # iframe으로 전환
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "ifrmBookStep")))
                        iframe_bookstep = driver.find_element(By.ID, "ifrmBookStep")
                        driver.switch_to.frame(iframe_bookstep)    

                        # 동의 체크
                        print("동의 체크")
                        # checkbox = driver.find_element(By.CSS_SELECTOR, "#checkAll input[type='checkbox']")
                        checkbox = driver.find_element(By.CSS_SELECTOR, "#checkAll[type='checkbox']")
                        checkbox.click()

                        # iframe 나오기
                        driver.switch_to.default_content()    

                        # 결제하기 버튼 누르기
                        print("결제하기 버튼 누름.")
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "LargeNextBtnImage")))
                        pay_button = driver.find_element(By.ID, "LargeNextBtnImage")
                        pay_button.click()    

                        # 카카오 페이 창 전환
                        # 새 창이나 탭이 열릴 때까지 기다림
                        WebDriverWait(driver, wait_sec).until(lambda d: len(d.window_handles) > 2)
                        window_handles = driver.window_handles
                        driver.switch_to.window(window_handles[2])

                        # 카톡결제 누르기
                        # iframe으로 전환
                        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "kakaoiframe")))
                        iframe_bookstep = driver.find_element(By.ID, "kakaoiframe")
                        driver.switch_to.frame(iframe_bookstep)    
                        
                        # 카톡결제 클릭
                        # '카톡결제' 버튼 찾기
                        # time.sleep(3)
                        # kakaotalk_btn = WebDriverWait(driver, 10).until(
                        #     EC.presence_of_element_located((By.XPATH, "//div[@class='kp-m-tab-header-item' and @id='카톡결제']"))
                        # )
                        # kakaotalk_btn.click()
                        kakaotalk_btn = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[@id='카톡결제' and contains(@class, 'kp-m-tab-header-item')]"))
                        )
                        kakaotalk_btn.click()
                        print("카톡결제9 클릭 성공")

                        phone_input = WebDriverWait(driver, wait_sec).until(
                            EC.presence_of_element_located((By.NAME, "phoneNumber"))
                        )
                        phone_input.clear()  # 기존 입력값 제거
                        phone_input.send_keys(kakao_phone_number)
                        print("휴대폰 번호 입력 완료")

                        # 생년월일 입력.
                        birth_input = WebDriverWait(driver, wait_sec).until(
                            EC.presence_of_element_located((By.NAME, "dateOfBirth"))
                        )
                        birth_input.clear()  # 기존 입력값 제거
                        birth_input.send_keys(kakao_birth_date)
                        print("생년월일 입력 완료")

                        # <button class="button-request btn_payask on">결제요청</button>
                        # 결제요청 클릭
                        # "결제요청" 버튼을 대기하고 클릭
                        # print(link.text)
                        # time.sleep(15)
                        pay_request_btn = WebDriverWait(driver, wait_sec).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'kp-m-button') and contains(., '결제요청')]"))
                        )
                        # time.sleep(3)
                        pay_request_btn.click()
                        now = datetime.now()
                        print(now,"결제요청 버튼 클릭 성공")
                        time.sleep(3600)
            else:
                print("스탠딩만 할거지??")
        driver.refresh()
        time.sleep(2)
    except Exception as e: 
        print(e)
        driver.refresh()
    #     if not is_have_seat:
    #         try:
    #             driver.refresh()
    #             continue
    #         except Exception as e:
    #             actions = ActionChains(driver)
    #             actions.send_keys(Keys.F5)
    #             actions.perform()
    #             continue
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".box ul li"))
    #     )
    #     area_list_items = driver.find_elements(By.CSS_SELECTOR, ".box ul li")
    #     is_have_seat=False
    #     # 각 리스트 항목의 텍스트에서 좌석 수를 추출하고, 2석 이상인 경우 링크를 클릭합니다.
    #     for item in area_list_items:
    #         text = item.text
    #         match = re.search(r'(\d+)석', text)
    #         if match:
    #             seat_count = int(match.group(1))  # 숫자 추출
    #             if seat_count >= wanted_seats_count:
    #                 print(f"{text} - 2석 이상 남음, 클릭합니다 {data_str}")
    #                 link = item.find_element(By.TAG_NAME, "a")
    #                 link.click()
    #                 is_have_seat=True
    #                 break  # 첫 번째로 발견된 2석 이상인 영역을 클릭한 후 반복문 탈출  #divSeatBox
    #     if not is_have_seat:
    #         driver.refresh()
    #         # time.sleep(1)
    #         # random_sleep_time = random.uniform(0.1, 0.3)
    #         # time.sleep(random_sleep_time)        
    #         continue  
        
    #         try:
    #             driver.refresh()

    #             continue
    #         except Exception as e:
    #             actions = ActionChains(driver)
    #             actions.send_keys(Keys.F5)
    #             actions.perform()
    #             continue
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.ID, "ifrmSeatDetail"))
    #     )

    #     # 'iframe' 요소로 전환합니다.
    #     driver.switch_to.frame("ifrmSeatDetail")

    #     # 이제 'iframe' 내부의 요소들에 접근할 수 있습니다.
    #     # 예를 들어, 'Seats' id를 가진 요소를 찾습니다.
    #     seats = driver.find_elements(By.ID, "Seats")

    #     # 'seats' 요소들을 처리하는 로직을 여기에 추가합니다.
    #     # 예를 들어, 각 요소의 텍스트를 출력할 수 있습니다.
    #     is_have_seat=False
    #     if len(seats)<2:
    #         print("애들 빠르다..")
    #     for i,seat in enumerate(seats):
    #         if i>0:
    #             print(seats[i].get_attribute("title"))
    #             if seats[i].location['y']==seats[i-1].location['y'] and seats[i].location['x']-seats[i-1].location['x']>10 and seats[i].location['x']-seats[i-1].location['x']<15:
    #                 # print(seats[i-1].get_attribute("title"))
    #                 seats[i-1].click()
    #                 seats[i].click()
    #                 print("클릭완료)")
    #                 is_have_seat=True
    #                 break
    #     if not is_have_seat:
    #         driver.refresh()
    #         # time.sleep(1)
    #         # random_sleep_time = random.uniform(0.1, 0.3)
    #         # time.sleep(random_sleep_time)        
    #         continue   
    #     driver.switch_to.default_content()
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.ID, "ifrmSeat"))
    #     )
    #     driver.switch_to.frame("ifrmSeat")
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.ID, "NextStepImage"))
    #     )
    #     NextStepImage = driver.find_elements(By.ID, "NextStepImage")
    #     NextStepImage[0].click()    
    # except Exception as e:
    #     try:
    #         driver.refresh()
    #         continue
    #     except Exception as e:
    #         driver.back()
    #         continue
        


#     ## 좌석 수 고르는 창

#     # 먼저 메인 컨텐츠로 전환
    # driver.switch_to.default_content()
    # # iframe으로 전환
    # WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "ifrmBookStep")))
    # iframe_bookstep = driver.find_element(By.ID, "ifrmBookStep")
    # driver.switch_to.frame(iframe_bookstep)

    # WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    # # <select> 요소 찾기
    # WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.NAME, "SeatCount")))
    # select_element = driver.find_element(By.NAME, "SeatCount")

    # # Select 객체 생성
    # select_object = Select(select_element)

    # # "2매" 선택 (옵션 값 "2" 사용)
    # select_object.select_by_value(f"{wanted_seats_count}")

    # # iframe_bookstep 작업 완료 후, 메인 페이지로 다시 전환
    # driver.switch_to.default_content()

    # # 다음 버튼 클릭
    # # 'SmallNextBtnLink' ID를 가진 <a> 요소 찾기 (다음 버튼)
    # WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "SmallNextBtnImage")))
    # # next_button = driver.find_element(By.XPATH, "//img[@src='//ticketimage.interpark.com/TicketImage/onestop/btn_next_02_on.gif']")
    # next_button = driver.find_element(By.ID, "SmallNextBtnImage")
    # next_button.click()

#     # 약관 동의
#     # iframe으로 전환
#     iframe_cert = driver.find_element(By.ID, "ifrmBookCertify")
#     driver.switch_to.frame(iframe_cert)

#     # 체크박스 요소 찾기
#     checkbox = driver.find_element(By.ID, "Agree")

#     # 체크박스가 체크되어 있지 않다면 클릭
#     if not checkbox.is_selected():
#         checkbox.click()

#     # 저장 버튼 찾기 (src 속성을 기반으로)
#     save_button = driver.find_element(By.XPATH, "//img[@src='http://ticketimage.interpark.com/TicketImage/event/110321/btn_pop_01.gif']")

#     # 저장 버튼 클릭
#     save_button.click()

#     # iframe 나오기.
#     driver.switch_to.default_content()

#     # 다음 버튼 클릭 (src 속성을 기반으로)
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "SmallNextBtnImage")))
#     # next_button = driver.find_element(By.XPATH, "//img[@src='//ticketimage.interpark.com/TicketImage/onestop/btn_next_02_on.gif']")
#     next_button = driver.find_element(By.ID, "SmallNextBtnImage")    
#     next_button.click()

#     # # 경고창 처리
#     # while True:
#     #     # 경고창 없으면 반복
#     #     if alert_check():
#     #         find_seat = False
#     #         break
#     #     if book_Delivery_check():
#     #         find_seat = True
#     #         break
#     #     print('로딩 중...')
#     #     time.sleep(0.2)
    
#     # if not find_seat:
#     #     continue
#     # else:
#     #     print("자리 차지 완료!")

#     try:
#         WebDriverWait(driver, wait_sec).until(EC.alert_is_present())
#         alert = driver.switch_to.alert
#         alert_text = alert.text  # 경고창의 내용을 가져옴
#         print("경고창 내용:", alert_text)
#         alert.accept()  # "확인" 버튼 클릭
#         find_seat = False
#         continue
#     except TimeoutException:
#         print("경고창이 없습니다.")

#     ## 생년월일 입력.
#     print("생년월일 입력")
#     # iframe으로 전환
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "ifrmBookStep")))
#     iframe_bookstep = driver.find_element(By.ID, "ifrmBookStep")
#     driver.switch_to.frame(iframe_bookstep)

# #     # 'YYMMDD' ID를 가진 <input> 요소 찾기
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "YYMMDD")))
#     input_element = driver.find_element(By.ID, "YYMMDD")

#     # 숫자 입력
#     input_element.send_keys(birth_date)    

#     # iframe 나오기
#     driver.switch_to.default_content()

#     # 다음 버튼 누르기
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "SmallNextBtnImage")))
#     next_button = driver.find_element(By.ID, "SmallNextBtnImage")
#     next_button.click()


#     ## 결제 선택
#     print("카카오페이 선택")
#     # iframe으로 전환
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "ifrmBookStep")))
#     iframe_bookstep = driver.find_element(By.ID, "ifrmBookStep")
#     driver.switch_to.frame(iframe_bookstep)

#     # "카카오" 라벨을 가진 라디오 버튼 찾기
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(), '카카오')]/preceding-sibling::input[@type='radio']")))
#     bank_transfer_radio = driver.find_element(By.XPATH, "//label[contains(text(), '카카오')]/preceding-sibling::input[@type='radio']")

#     # 라디오 버튼 클릭
#     bank_transfer_radio.click()  

# #     # # 은행 선택
# #     # print("은행 선택")
# #     # # 'BankCode' ID를 가진 <select> 요소 찾기
# #     # select_element = driver.find_element(By.ID, "BankCode")

# #     # # Select 객체 생성
# #     # select_object = Select(select_element)

# #     # # "국민은행" 선택 (옵션 값 "38051" 사용)
# #     # select_object.select_by_value("38051")

# #     # iframe 나오기
#     driver.switch_to.default_content()
    
# #     # 다음 버튼 누르기
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "SmallNextBtnImage")))
#     next_button = driver.find_element(By.ID, "SmallNextBtnImage")
#     next_button.click()    


# #     ## 결제하기
#     print("결제하기")
#     # iframe으로 전환
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "ifrmBookStep")))
#     iframe_bookstep = driver.find_element(By.ID, "ifrmBookStep")
#     driver.switch_to.frame(iframe_bookstep)    

#     # 동의 체크
#     print("동의 체크")
#     # checkbox = driver.find_element(By.CSS_SELECTOR, "#checkAll input[type='checkbox']")
#     checkbox = driver.find_element(By.CSS_SELECTOR, "#checkAll[type='checkbox']")
#     checkbox.click()

#     # iframe 나오기
#     driver.switch_to.default_content()    

#     # 결제하기 버튼 누르기
#     print("결제하기 버튼 누름.")
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "LargeNextBtnImage")))
#     pay_button = driver.find_element(By.ID, "LargeNextBtnImage")
#     pay_button.click()    

#     # 카카오 페이 창 전환
#     # 새 창이나 탭이 열릴 때까지 기다림
#     WebDriverWait(driver, wait_sec).until(lambda d: len(d.window_handles) > 2)
#     window_handles = driver.window_handles
#     driver.switch_to.window(window_handles[2])

#     # 카톡결제 누르기
#     # iframe으로 전환
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "kakaoiframe")))
#     iframe_bookstep = driver.find_element(By.ID, "kakaoiframe")
#     driver.switch_to.frame(iframe_bookstep)    
    
#     # 카톡결제 클릭
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'kakaotalk')]")))
#     kakaotalk_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'kakaotalk')]")
#     # kakaotalk_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'button-menu') and contains(@class, 'kakaotalk')]")
#     kakaotalk_btn.click()

#     # 휴대폰 번호 입력.
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "userPhone")))
#     input_element = driver.find_element(By.ID, 'userPhone')
#     time.sleep(1)
#     input_element.send_keys(kakao_phone_number)

#     # 생년월일 입력.
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "userBirth")))
#     input_element = driver.find_element(By.ID, 'userBirth')
#     input_element.send_keys(kakao_birth_date)

#     # <button class="button-request btn_payask on">결제요청</button>
#     # 결제요청 클릭
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'btn_payask') and contains(@class, 'on')]")))
#     pay_request_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'btn_payask') and contains(@class, 'on')]")
#     pay_request_btn.click()

#     break

# print('end')