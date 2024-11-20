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
from selenium.webdriver import ActionChains

from ..config.group_mapping import GroupMappingConfig
from ..utils.logger import log_manager

class FeishuMonitor:
    """飞书监控类"""
    
    def __init__(self, source_groups: list, group_mapping_config: GroupMappingConfig):
        """初始化"""
        self.source_groups = source_groups
        self.group_mapping_config = group_mapping_config
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
            
            # 获取消息列表
            messages = []
            try:
                # 使用XPath查找消息元素
                message_elements = self.driver.find_elements(By.XPATH, "//span[@class='text-only']")
                
                for msg_element in message_elements:
                    try:
                        # 获取消息内容
                        content = msg_element.get_attribute('innerText')
                        if not content:
                            continue
                            
                        # 使用当前时间作为消息时间
                        msg_time = datetime.now()
                        
                        # 如果是新消息则添加到列表
                        if group_name not in self.last_message_time or msg_time > self.last_message_time[group_name]:
                            messages.append({
                                'content': content,
                                'time': msg_time
                            })
                            
                    except Exception as e:
                        log_manager.error(f"解析消息失败: {str(e)}")
                        continue
                        
            except Exception as e:
                log_manager.error(f"获取消息列表失败: {str(e)}")
                return []
                
            if messages:
                self.last_message_time[group_name] = messages[-1]['time']
                
            return messages
            
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
            time.sleep(2)  # 等待群组加载
            
            try:
                # 使用body元素发送按键，这样可以避免直接操作输入框
                body = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 确保焦点在页面上
                body.click()
                time.sleep(0.5)
                
                # 直接发送按键事件到body
                for char in message['content']:
                    body.send_keys(char)
                    time.sleep(0.05)  # 添加少量延迟模拟真实输入
                
                time.sleep(0.5)
                
                # 查找并点击发送按钮
                send_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button.ud__button--icon .send__button"))
                )
                
                # 确保按钮可见和可点击
                self.driver.execute_script("arguments[0].scrollIntoView(true);", send_button)
                time.sleep(0.5)
                
                # 尝试使用JavaScript点击按钮
                self.driver.execute_script("arguments[0].click();", send_button)
                
                log_manager.info(f"消息已转发到群 [{target_group}]: {message['content'][:50]}...")
                time.sleep(1)  # 等待消息发送完成
                return True
                
            except Exception as e:
                log_manager.error(f"发送消息失败: {str(e)}")
                log_manager.error(f"消息内容: {message['content']}")
                # 尝试获取发送按钮状态
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, "button.ud__button--icon .send__button")
                    button_classes = send_button.get_attribute("class")
                    log_manager.error(f"发送按钮状态: {button_classes}")
                except:
                    log_manager.error("无法获取发送按钮状态")
                return False
                
        except Exception as e:
            log_manager.error(f"转发消息到群 {target_group} 失败: {str(e)}")
            return False
            
    def start(self):
        """开始监控"""
        self.is_running = True
        log_manager.info("开始监控消息...")
        
        while self.is_running:
            try:
                for source_group in self.source_groups:
                    # 获取新消息
                    messages = self.get_new_messages(source_group)
                    if not messages:
                        continue
                        
                    # 获取目标群列表
                    target_groups = self.group_mapping_config.get_target_groups(source_group)
                    if not target_groups:
                        log_manager.warning(f"群组 {source_group} 未配置目标群")
                        continue
                        
                    # 转发消息到所有目标群
                    for message in messages:
                        for target_group in target_groups:
                            self.forward_message(message, target_group)
                            
                time.sleep(5)  # 等待一段时间再次检查
                
            except Exception as e:
                log_manager.error(f"监控过程发生错误: {str(e)}")
                time.sleep(10)  # 发生错误时等待较长时间
                
    def stop(self):
        """停止监控"""
        self.is_running = False
        if self.driver:
            self.driver.quit()
            self.driver = None
        log_manager.info("监控已停止")
