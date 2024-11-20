"""
飞书监控模块
"""
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

logger = logging.getLogger(__name__)

class FeishuMonitor:
    """飞书监控类"""
    
    def __init__(self, source_groups, target_group):
        """初始化"""
        self.source_groups = source_groups
        self.target_group = target_group
        self.is_running = False
        self.driver = None
        self.last_message_time = {}  # 用于存储每个群的最后消息时间
        
    def setup_browser(self):
        """启动浏览器并打开飞书"""
        try:
            # 初始化浏览器
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
            
            # 打开飞书
            self.driver.get("https://www.feishu.cn/messenger/")
            logger.info("浏览器已启动，请扫码登录...")
            
            # 等待消息列表出现，表示登录成功
            WebDriverWait(self.driver, 300).until(
                EC.presence_of_element_located((By.CLASS_NAME, "_2b17aec6"))
            )
            logger.info("登录成功")
            return True
            
        except Exception as e:
            logger.error(f"启动浏览器失败: {str(e)}")
            if self.driver:
                self.driver.quit()
            return False
        
    def find_group_by_name(self, group_name):
        """
        通过群名查找群
        :param group_name: 群名
        :return: 群元素
        """
        try:
            # 使用特定的类名和文本内容查找群组
            groups = self.driver.find_elements(By.CLASS_NAME, "_2b17aec6")
            for group in groups:
                if group.text == group_name:
                    return group
                    
            # 如果直接查找失败，尝试使用XPath
            xpath = f"//*[contains(@class, '_2b17aec6') and text()='{group_name}']"
            return WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
        except Exception as e:
            logger.error(f"查找群 {group_name} 失败: {str(e)}")
            return None
            
    def get_messages(self, group):
        """
        获取群消息
        :param group: 群元素
        :return: 消息列表
        """
        try:
            # 点击进入群
            group.click()
            time.sleep(1)  # 等待消息加载
            
            # 获取消息元素
            message_elements = self.driver.find_elements(By.CSS_SELECTOR, '[class*="message-content"]')
            messages = []
            
            for msg_elem in message_elements:
                try:
                    # 获取消息时间戳
                    timestamp_elem = msg_elem.find_element(By.XPATH, './ancestor::div[contains(@class, "msg-item")]//time')
                    msg_time = timestamp_elem.get_attribute('title')  # 获取完整的时间字符串
                    msg_timestamp = datetime.strptime(msg_time, "%Y-%m-%d %H:%M:%S")
                    
                    # 获取消息内容
                    msg_text = msg_elem.text.strip()
                    
                    if msg_text:
                        messages.append({
                            'text': msg_text,
                            'timestamp': msg_timestamp
                        })
                except Exception as e:
                    logger.error(f"处理单条消息时出错: {str(e)}")
                    continue
            
            # 按时间戳排序
            messages.sort(key=lambda x: x['timestamp'])
            
            # 筛选新消息
            group_name = group.text
            last_time = self.last_message_time.get(group_name)
            new_messages = []
            
            for msg in messages:
                if not last_time or msg['timestamp'] > last_time:
                    new_messages.append(msg['text'])
                    self.last_message_time[group_name] = msg['timestamp']
            
            return new_messages
            
        except Exception as e:
            logger.error(f"获取消息失败: {str(e)}")
            return []
            
    def forward_message(self, message, target_group_name):
        """
        转发消息
        :param message: 消息内容
        :param target_group_name: 目标群名
        """
        try:
            # 查找并进入目标群
            target_group = self.find_group_by_name(target_group_name)
            if target_group:
                target_group.click()
                time.sleep(1)
                
                # 找到输入框并发送消息
                input_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[contenteditable="true"]'))
                )
                input_box.clear()
                input_box.send_keys(message)
                time.sleep(0.5)
                input_box.send_keys(Keys.ENTER)
                
                logger.info(f"消息转发成功")
                
        except Exception as e:
            logger.error(f"转发消息失败: {str(e)}")
            
    def start_monitoring(self):
        """开始监控消息"""
        try:
            self.is_running = True
            logger.info("开始监控消息...")
            
            # 初始化每个源群的最后消息时间
            for source_group in self.source_groups:
                self.last_message_time[source_group] = datetime.now()
            
            # 开始监控
            while self.is_running:
                for source_group in self.source_groups:
                    if not self.is_running:
                        break
                        
                    group = self.find_group_by_name(source_group)
                    if group:
                        messages = self.get_messages(group)
                        for message in messages:
                            if not self.is_running:
                                break
                            self.forward_message(message, self.target_group)
                    
                    time.sleep(5)  # 避免过于频繁的检查
                
        except Exception as e:
            logger.error(f"监控过程发生错误: {str(e)}")
            raise
            
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        logger.info("停止监控消息")
        
    def cleanup(self):
        """清理资源"""
        if self.driver:
            self.driver.quit()
            logger.info("浏览器已关闭")
