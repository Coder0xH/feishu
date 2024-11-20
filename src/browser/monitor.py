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
            time.sleep(1)  # 减少等待时间
            
            try:
                # 定位输入框区域
                input_area = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'innerdocbody')]"))
                )
                
                # 点击输入框获取焦点
                input_area.click()
                time.sleep(0.2)
                
                # 输入消息
                input_area.send_keys(message['content'])
                time.sleep(0.3)  # 短暂等待确保消息输入完成
                
                # 发送消息 (模拟Enter键)
                input_area.send_keys(Keys.ENTER)
                time.sleep(0.2)  # 等待消息发送
                
                log_manager.info(f"消息已转发到群 [{target_group}]: {message['content'][:50]}...")
                return True
                
            except Exception as e:
                log_manager.error(f"发送消息失败: {str(e)}")
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
