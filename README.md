# HowlerBot   [![Wechaty Contributor Program](https://img.shields.io/badge/Wechaty-Contributor%20Program-green.svg)](https://wechaty.js.org/docs/contributing/)
HowlerBot 定位是生活帮手，陪玩，整蛊等多元化的机器人。由于目前智商感人，有时候让人抓狂！不过她会成长，所以请给她点耐心，让我们见证脑残儿童的成长吧！
## Prerequisites
1. 需要获取 `Wechaty Puppet Service` 的 `token` 
   1. [有关 token 的说明](https://wechaty.js.org/docs/puppet-services/#get-a-token)
   2. [申请免费试用地址](http://pad-local.com/#/tokens)
2. `python-wechaty` 是 `wechaty` 的 python 客户端
   1. github 地址: https://github.com/wechaty/python-wechaty
3. `paddlepaddle`, `paddlenlp` (用于一些本地模型推理，后期会分离出去，采用远端调用的方式请求，本地弊端太多)
   1. paddlepaddle github: https://github.com/PaddlePaddle/Paddle
   2. paddlenlp github: https://github.com/PaddlePaddle/paddlenlp

## Note
* 需要部署一个 `wechaty puppet service` 的 `gateway` 服务
	* 因为 wechaty 本身是 ts 实现的，为了支持多语言（例如本例的 python 调用）需要部署类似充当 "翻译" 的 proxy 服务，我们称为 gateway.
    * 具体步骤可以参见：https://python-wechaty.readthedocs.io/zh_CN/latest/introduction/use-padlocal-protocol/
    * 机器资源可以是你的本地电脑，也可以是云厂商的云机器，这里我是”薅“ 了百度云的轻量级服务器，[新人活动 89 元/年](https://cloud.baidu.com/campaign/2021autdiscount/index.html?track=cp:npinzhuan|pf:PC|pp:npinzhuan-biaoti|pu:wenzineirong|ci:21phsy|kw:10314815)，还是比较划算的。
    * 购置好机器后，安装 docker, 然后执行这个 [start_puppet_service_gateway.sh](https://github.com/jiaqianjing/HowlerBot/blob/main/puppet_service_gateway/start_puppet_service_gateway.sh) (注意启动前，打开该文件，替换自己的 token)
 * `查询天气` 功能这里调用是的[百度云-云市场](https://market.baidu.com/)关于查询天气的第三方 API，在 `header` 中使用了鉴权的 `appcode` 这里脱敏了，如果需要此功能，需要用户自行解决。 
 * 其他没啥注意的，按照 github 中的 readme 操作即可。

## Usage
### 如何启动
   1. 需要修改 `main.py` 中环境变量 `WECHATY_PUPPET_SERVICE_TOKEN` 对应你的 puppet service gateway 的 token. [相关内容见 python-wechaty 文档](https://python-wechaty.readthedocs.io/zh_CN/latest/introduction/use-padlocal-protocol/)
   
   2. 安装依赖
      ```python
      pip install -r requirements
      ```
   3. 执行启动命令
      ```bash
      python main.py
      ```

### 目前机器人支持以下场景和指令
1. `#你会啥`
   微信内推送帮助指令

2. `#唠嗑了`
   开启闲聊模式，可以和你侃天侃地，你说一句，她回一句，不过不是简单一问一答的句式，而是她会在对话的过程中，主动询问，从而是整个聊天过程更加生动。从进入闲聊模式后，就记录了此次聊天的全部上下文在内存中（未来可以考虑引入缓存的管理算法，避免单次聊天内容过长，导致内存溢出），因此，在单轮闲聊模式中不会出现内容断层的现象。此外，她具备一些基础 knowledge，不会显得过于傻。通过 `#拜拜` 指令进行关闭闲聊模式，此时会释放此次对话的上下文内容。 

3. `#拜拜`
   关闭闲聊模式。（释放对话上下文信息）

4. `#天气 xxx`
   查询天气预报，例如 `#天气 北京`。目前支持国内。

5. `#干饭`
   会发出`饿了吗`外卖优惠券。除了使用该指令触发，还会定时每天 10 点半，主动提醒，让你错峰订餐，避免高峰等待过长时间用膳。

6. 进群欢迎语
   当有新朋友进入机器人所在的群的时候，机器人会主动发送欢迎的消息。

## Demo
### B 站视频
   
   <iframe src="//player.bilibili.com/player.html?aid=250237547&bvid=BV1wv411P78p&cid=398500521&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true" width=600 height=800> </iframe>

### 截图
* 帮助指令
  ![](./img/demo-05.png)

* 进群欢迎语  
  ![](./img/demo-01.png)

* 闲聊  
  ![](./img/demo-02.png)

* 查询天气  
  ![](./img/demo-03.png)

* 获取外卖优惠码  
  ![](./img/demo-04.png)


## Citation
```
@misc{wechaty,
  author = {Huan LI, Rui LI},
  title = {Wechaty: Conversational RPA SDK for Chatbot Makers},
  year = {2016},
  publisher = {GitHub},
  journal = {GitHub Repository},
  howpublished = {\url{https://github.com/wechaty/wechaty}},
}
```
