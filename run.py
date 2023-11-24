from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
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
import pytesseract
import threading
wait_sec = 1
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# 예매할 자리 수 (최대 2매)
wanted_seats_count = 2

# 인터파크 아이디 생년월일
birth_date = "960922"

# 결제할 카카오톡 정보
# 핸드폰 번호
kakao_phone_number = "01048425162"
# 생년월일
kakao_birth_date = "941122"

driver = webdriver.Chrome()
def chapcha():    
    try:
        while True:
            WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.ID, "imgCaptcha")))
            capcha_layer = driver.find_element(By.ID, 'imgCaptcha')
            if capcha_layer.is_displayed():
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
                    element_to_click = driver.find_element(By.XPATH, "//*[@id='divRecaptcha']/div[1]/div[4]/a[2]")

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
            else:
               break 
    except TimeoutException:
        print("Captcha 요소가 없어서 계속 진행")



def puzzle():
    
    try:
        while True:
            WebDriverWait(driver,0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "canvas")))
            canvas_element = driver.find_element(By.CSS_SELECTOR, 'canvas')
            if canvas_element.is_displayed():
                img_data = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas_element)
                og_image=cv2.imread("moda.jpg")
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
                    # print("클리어")
                    break
                else:
                    print("다시")
            else:
                break
            
    except TimeoutException:
        print("Canvas 요소가 없어서 계속 진행")
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
driver.get('https://ticket.interpark.com/Gate/TPLogin.asp?CPage=B&MN=Y&tid1=main_gnb&tid2=right_top&tid3=login&tid4=login')

# 사용자가 직접 로그인
input("로그인 한 후에는 'y'를 입력하고 Enter 누르세요.")

# driver.get('https://tickets.interpark.com/goods/23016975') #황영웅
driver.get('https://tickets.interpark.com/goods/23016176') #모다



# 'popupCloseBtn is-bottomBtn' 클래스를 가진 버튼을 찾습니다.
close_button = WebDriverWait(driver, wait_sec).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".popupCloseBtn.is-bottomBtn"))
)

# 버튼 클릭
close_button.click()
# '30' 텍스트를 포함하는 `li` 요소를 찾습니다. 'disabled'나 'muted' 클래스를 가지지 않은 요소를 선택합니다.
li_30 = WebDriverWait(driver, wait_sec).until(
# EC.element_to_be_clickable((By.XPATH, "//ul[@data-view='days']/li[text()='25' and not(contains(@class, 'disabled')) and not(contains(@class, 'muted'))]"))
EC.element_to_be_clickable((By.XPATH, "//*[@id='productSide']/div/div[1]/div[1]/div[2]/div/div/div/div/ul[3]/li[30]"))
)

# 해당 요소를 클릭합니다.
li_30.click()

button = WebDriverWait(driver, wait_sec).until(
    EC.element_to_be_clickable((By.XPATH, "//*[@id='productSide']/div/div[2]/a[1]/span"))
    # EC.element_to_be_clickable((By.XPATH, "//*[@id='productSide']/div/div[2]/a[1]"))
)
while True:
    if (button.text!="예매하기"):
        button = WebDriverWait(driver, wait_sec).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='productSide']/div/div[2]/a[1]/span"))
            # EC.element_to_be_clickable((By.XPATH, "//*[@id='productSide']/div/div[2]/a[1]"))
        )
    else :
        break            
# 요소 클릭
button.click()
print("dd")






## 좌석 선택 창
# 새 창 전환하기
# 새 창이나 탭이 열릴 때까지 기다림
WebDriverWait(driver, wait_sec).until(lambda d: len(d.window_handles) > 1)
window_handles = driver.window_handles
driver.switch_to.window(window_handles[1])

# find_seat = False
capcha_check=True
while True:
    # iframe으로 전환
    # 나올 때까지 기다리기
    # # 새 창이나 탭의 로딩을 기다림
    # WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "ifrmSeat")))
    iframe_seat = driver.find_element(By.ID, "ifrmSeat")
    driver.switch_to.frame(iframe_seat)

#     # 보안문자 넘어가기
#     # display: none; 검사
    
    chapcha()
    puzzle()
    
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "PlayDate")))
    driver.execute_script("document.getElementById('PlayDate').value = '20231230';")
    driver.execute_script("document.getElementById('PlaySeq').value = '001';")
    WebDriverWait(driver, 60).until(
        EC.presence_of_all_elements_located((By.XPATH, "//tr[@id='GradeRow']/td/div/span[@class='select']"))
    )

    # 요소들이 로드되었으므로 이제 찾을 수 있습니다.
    seat_grades = driver.find_elements(By.XPATH, "//tr[@id='GradeRow']/td/div/span[@class='select']")
    is_have_seat=False
    for seat_grade in seat_grades:
        text = seat_grade.text
        seat_count = int(re.search(r'\d+', text).group())  # 숫자 추출
        print(f"{text} - {seat_count}석  남음")
        if seat_count >= wanted_seats_count:
            print(f"{text} - {wanted_seats_count}석 이상 남음")
            is_have_seat=True
            seat_grade.click()
            break
    if not is_have_seat:
        driver.refresh()
        # time.sleep(1)
        # random_sleep_time = random.uniform(0.01, 0.3)
        # time.sleep(random_sleep_time)        
        continue    
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".box ul li"))
    )
    area_list_items = driver.find_elements(By.CSS_SELECTOR, ".box ul li")

    # 각 리스트 항목의 텍스트에서 좌석 수를 추출하고, 2석 이상인 경우 링크를 클릭합니다.
    for item in area_list_items:
        text = item.text
        match = re.search(r'(\d+)석', text)
        if match:
            seat_count = int(match.group(1))  # 숫자 추출
            if seat_count >= wanted_seats_count:
                print(f"{text} - 2석 이상 남음, 클릭합니다.")
                link = item.find_element(By.TAG_NAME, "a")
                link.click()
                break  # 첫 번째로 발견된 2석 이상인 영역을 클릭한 후 반복문 탈출  #divSeatBox
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ifrmSeatDetail"))
    )

    # 'iframe' 요소로 전환합니다.
    driver.switch_to.frame("ifrmSeatDetail")

    # 이제 'iframe' 내부의 요소들에 접근할 수 있습니다.
    # 예를 들어, 'Seats' id를 가진 요소를 찾습니다.
    seats = driver.find_elements(By.ID, "Seats")

    # 'seats' 요소들을 처리하는 로직을 여기에 추가합니다.
    # 예를 들어, 각 요소의 텍스트를 출력할 수 있습니다.
    for i,seat in enumerate(seats):
        if i>0:
            if seats[i].location['y']==seats[i-1].location['y'] and seats[i].location['x']-seats[i-1].location['x']>10 and seats[i].location['x']-seats[i-1].location['x']<15:
                print(seats[i].get_attribute("title"))
                print(seats[i-1].get_attribute("title"))
                seats[i-1].click()
                seats[i].click()
                print("클릭클릭")
                is_have_seat=True
                break
    if not is_have_seat:
        driver.refresh()
        # time.sleep(1)
        # random_sleep_time = random.uniform(0.1, 0.3)
        # time.sleep(random_sleep_time)        
        continue   
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ifrmSeat"))
    )
    driver.switch_to.frame("ifrmSeat")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "NextStepImage"))
    )
    NextStepImage = driver.find_elements(By.ID, "NextStepImage")
    NextStepImage[0].click()    
#     # 'display: none;'이 포함되어 있는지 확인<span class="SeatN" id="Seats" name="Seats" style="background-color:#7C68EE;" title="[SR석] FLOOR-타구역 8열-8" onclick="SelectSeat(this,'1','FLOOR','타구역 8열','8','012','SR석')" value="N" seatinfo="" rowidx="0" colidx="0" limitcnt="0"><!----></span>
#     if "display: none;" not in style_attribute:
#         # print("capcha_layer는 표시되어 있습니다.")    
#         WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.CLASS_NAME, "capchaBtns")))
#         fncheckbtn = driver.find_element(By.CLASS_NAME, 'capchaBtns')

#         # JavaScript를 사용하여 onclick 이벤트 변경
#         script = """
#         var element = document.querySelector('.capchaBtns a');
#         if (element) {
#             element.setAttribute('onclick', 'fnCheckOK()');
#         }
#         """
#         driver.execute_script(script)

#         fncheckbtn.click()

#     # 남은 자리 확인.
#     # .groundList 클래스 아래의 .list 클래스를 가진 요소 찾기
#     WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".groundList .list")))
#     # WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
#     # seat_list_element = driver.find_element(By.CSS_SELECTOR, ".groundList .list")

#     # 0이 아닌 곳이 있나 확인.
#     # JavaScript를 사용하여 rc 속성이 0이 아닌 <a> 요소 찾기
#     available_seats_script = """
#     var links = document.querySelectorAll('.groundList .list a');
#     var availableSeats = [];
#     for (var i = 0; i < links.length; i++) {
#         if (links[i].getAttribute('rc') != '0') {
#             availableSeats.push(links[i]);
#         }
#     }
#     return availableSeats;
#     """
#     available_seats = driver.execute_script(available_seats_script)

#     # available_seats 배열에는 rc 속성이 0이 아닌 <a> 요소들이 포함되어 있음
#     # 예를 들어, 첫 번째 요소에 대한 정보를 출력
#     if len(available_seats) > 0:
#         # 현재 날짜와 시간을 가져오기
#         current_datetime = datetime.now()
#         # 문자열 형식으로 출력하기
#         formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")        
#         print(f"좌석 발견!! {formatted_datetime}")
#         for available_seat in available_seats:
#             rc = available_seats[0].get_attribute('rc')
#             seat_text = available_seats[0].find_element(By.CSS_SELECTOR, 'span.red').text
#             print(f"  rc={rc}, {seat_text}")

#             # 숫자만 추출하는 정규 표현식 패턴
#             pattern = r'\d+'
#             if re.search(pattern, seat_text):
#                 num_seats = int(re.search(pattern, seat_text).group())
#             else:
#                 num_seats = 0

#             # '2'를 포함하는 텍스트를 발견한 경우 해당 좌석 클릭
#             if num_seats >= wanted_seats_count:
#                 print("\n자동 배정 진행!")
#                 available_seat.click()
#                 find_seat = True
#                 break
#     # else:
#     #     print("좌석 없음. 새로고침.")
    
#     if not find_seat:
#         # driver.switch_to.default_content()
#         driver.refresh()
#         # time.sleep(1)
#         random_sleep_time = random.uniform(0.01, 0.1)
#         time.sleep(random_sleep_time)        
#         continue
    
#     # 자리 찾음.
#     # 자동 배정 버튼 클릭
#     auto_assign_button = driver.find_element(By.XPATH, "//a[img[@src='//ticketimage.interpark.com/TicketImage/onestop/kbo_twoBtn_1.gif']]")
#     auto_assign_button.click()    


#     ## 좌석 수 고르는 창

#     # 먼저 메인 컨텐츠로 전환
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

#     # # 은행 선택
#     # print("은행 선택")
#     # # 'BankCode' ID를 가진 <select> 요소 찾기
#     # select_element = driver.find_element(By.ID, "BankCode")

#     # # Select 객체 생성
#     # select_object = Select(select_element)

#     # # "국민은행" 선택 (옵션 값 "38051" 사용)
#     # select_object.select_by_value("38051")

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
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'kakaotalk')]")))
    kakaotalk_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'kakaotalk')]")
    # kakaotalk_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'button-menu') and contains(@class, 'kakaotalk')]")
    kakaotalk_btn.click()

    # 휴대폰 번호 입력.
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "userPhone")))
    input_element = driver.find_element(By.ID, 'userPhone')
    time.sleep(1)
    input_element.send_keys(kakao_phone_number)

    # 생년월일 입력.
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "userBirth")))
    input_element = driver.find_element(By.ID, 'userBirth')
    input_element.send_keys(kakao_birth_date)

    # <button class="button-request btn_payask on">결제요청</button>
    # 결제요청 클릭
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'btn_payask') and contains(@class, 'on')]")))
    pay_request_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'btn_payask') and contains(@class, 'on')]")
    pay_request_btn.click()

#     break

# print('end')