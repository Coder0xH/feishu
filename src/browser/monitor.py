"""
飞书监控模块
"""
import time
import logging
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

from ..config.group_mapping import GroupMappingConfig
from ..utils.logger import log_manager

class FeishuMonitor:
    """飞书监控类"""
    
    def __init__(self, driver, group_mapping_config):
        """初始化监控器"""
        self.driver = driver
        self.group_mapping_config = group_mapping_config
        self.source_groups = group_mapping_config.get_source_groups() if group_mapping_config else []
        self.is_running = False
        self.last_message_content = {}  # 用于存储每个群组最后一条消息的内容
        
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
            log_manager.info("浏览器已启动，请扫码登录...")
            
            # 等待消息列表出现，表示登录成功
            WebDriverWait(self.driver, 300).until(
                EC.presence_of_element_located((By.CLASS_NAME, "_2b17aec6"))
            )
            log_manager.info("登录成功")
            return True
            
        except Exception as e:
            log_manager.error(f"启动浏览器失败: {str(e)}")
            if self.driver:
                self.driver.quit()
            return False
            
    def find_group_by_name(self, group_name):
        """查找群组"""
        try:
            # 直接使用XPath查找群组元素
            xpath = f"//div[@class='_2b17aec6'][text()='{group_name}']"
            group = self.driver.find_element(By.XPATH, xpath)
            return group
            
        except Exception as e:
            log_manager.error(f"查找群组 {group_name} 失败: {str(e)}")
            return None
            
    def get_new_messages(self, group_name):
        """获取群组新消息"""
        try:
            group = self.find_group_by_name(group_name)
            if not group:
                log_manager.error(f"未找到群组: {group_name}")
                return []
                
            # 点击进入群组
            group.click()
            time.sleep(1)  # 等待群组加载
            
            try:
                # 获取最新的消息元素
                message_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'message-content')]")
                if not message_elements:
                    return []
                
                # 只处理最新的一条消息
                latest_message = message_elements[-1]
                
                try:
                    # 检查是否是图片消息
                    image_element = latest_message.find_elements(By.XPATH, ".//img[contains(@class, 'msg-image')]")
                    if image_element:
                        # 获取发送者名称
                        try:
                            sender_element = latest_message.find_element(By.XPATH, ".//div[contains(@class, 'message-info__inner')]//span[contains(@class, 'message-info-name--clickable')]")
                            sender_name = sender_element.get_attribute('innerText').strip()
                        except NoSuchElementException:
                            sender_name = "未知用户"
                        
                        formatted_content = f"{sender_name}: [图片]"
                        
                        return [{
                            'content': formatted_content,
                            'sender': sender_name,
                            'raw_content': '[图片]',
                            'time': datetime.now(),
                            'type': 'image'
                        }]
                    
                    # 获取文本内容
                    text_element = latest_message.find_element(By.XPATH, ".//div[contains(@class, 'richTextContainer')]//span[contains(@class, 'text-only')]")
                    content = text_element.get_attribute('innerText').strip()
                    
                    # 获取发送者名称
                    try:
                        sender_element = latest_message.find_element(By.XPATH, ".//div[contains(@class, 'message-info__inner')]//span[contains(@class, 'message-info-name--clickable')]")
                        sender_name = sender_element.get_attribute('innerText').strip()
                    except NoSuchElementException:
                        sender_name = "未知用户"
                    
                    # 格式化消息内容
                    formatted_content = f"{sender_name}: {content}"
                    
                    # 如果已经发送过这条消息，则跳过
                    if group_name in self.last_message_content and self.last_message_content[group_name] == formatted_content:
                        return []
                    
                    # 更新最后发送的消息内容
                    self.last_message_content[group_name] = formatted_content
                    
                    return [{
                        'content': formatted_content,
                        'sender': sender_name,
                        'raw_content': content,
                        'time': datetime.now(),
                        'type': 'text'
                    }]
                    
                except Exception as e:
                    log_manager.error(f"解析消息内容失败: {str(e)}")
                    return []
                    
            except Exception as e:
                log_manager.error(f"获取消息列表失败: {str(e)}")
                return []
                
        except Exception as e:
            log_manager.error(f"获取群组 {group_name} 消息失败: {str(e)}")
            return []
            
    def forward_message(self, message, target_group):
        """转发消息到目标群"""
        try:
            # 查找目标群
            group = self.find_group_by_name(target_group)
            if not group:
                log_manager.error(f"未找到目标群: {target_group}")
                return False
                
            # 点击进入目标群
            group.click()
            time.sleep(1)
            
            try:
                # 如果是图片消息，发送[图片]文本
                if message.get('type') == 'image':
                    input_area = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'innerdocbody')]"))
                    )
                    input_area.click()
                    time.sleep(0.2)
                    input_area.send_keys("[图片]")
                    time.sleep(0.3)
                    input_area.send_keys(Keys.ENTER)
                    log_manager.info(f"图片消息已转发到群 [{target_group}]")
                    return True
                
                # 文本消息处理
                input_area = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'innerdocbody')]"))
                )
                
                # 点击输入框获取焦点
                input_area.click()
                time.sleep(0.2)
                
                # 输入消息
                input_area.send_keys(message['content'])
                time.sleep(0.3)
                
                # 发送消息
                input_area.send_keys(Keys.ENTER)
                time.sleep(0.2)
                
                log_manager.info(f"消息已转发到群 [{target_group}]: {message['content'][:50]}...")
                return True
                
            except Exception as e:
                log_manager.error(f"发送消息失败: {str(e)}")
                log_manager.error(f"原始消息内容: {message['content']}")
                return False
                
        except Exception as e:
            log_manager.error(f"转发消息到群 {target_group} 失败: {str(e)}")
            return False
            
    def start(self):
        """开始监控"""
        try:
            while True:
                # 遍历配置的群组映射
                for source_group in self.source_groups:
                    try:
                        # 获取源群组的新消息
                        messages = self.get_new_messages(source_group)
                        
                        # 转发新消息到目标群组
                        target_groups = self.group_mapping_config.get_target_groups(source_group)
                        if not target_groups:
                            log_manager.warning(f"群组 {source_group} 未配置目标群")
                            continue
                        for message in messages:
                            for target_group in target_groups:
                                if self.forward_message(message, target_group):
                                    time.sleep(0.5)  # 消息发送间隔
                            
                    except Exception as e:
                        log_manager.error(f"处理群组 {source_group} 失败: {str(e)}")
                        continue
                        
                time.sleep(1)  # 减少轮询间隔
                
        except KeyboardInterrupt:
            log_manager.info("监控已停止")
        except Exception as e:
            log_manager.error(f"监控异常: {str(e)}")
            
    def stop(self):
        """停止监控"""
        self.is_running = False
        if self.driver:
            self.driver.quit()
            self.driver = None
        log_manager.info("监控已停止")
