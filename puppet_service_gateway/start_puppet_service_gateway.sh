# 设置环境变量

export WECHATY_LOG="verbose"

# puppet 协议类型
export WECHATY_PUPPET="wechaty-puppet-padlocal"

# 用于 padlocal 服务供应商的 token 认证 (需要付费)
# 申请地址: http://pad-local.com
export WECHATY_PUPPET_PADLOCAL_TOKEN="puppet_padlocal_ee68888f722645588127f0773dbcb9bd"

# 本地网关服务暴露的端口
export WECHATY_PUPPET_SERVER_PORT="9001"

# 用于本地网关的 token 认证
# 可使用代码随机生成UUID：python -c "import uuid;print(uuid.uuid4());"
export WECHATY_TOKEN="60788d8e-4ea7-4d81-9349-8b0d697866b1"

docker run -ti \
  --restart=always \
  --network host \
  --name wechaty_puppet_service_token_gateway \
  -v $PWD/bot:/bot \
  -d \
  -e WECHATY_LOG \
  -e WECHATY_PUPPET \
  -e WECHATY_PUPPET_PADLOCAL_TOKEN \
  -e WECHATY_PUPPET_SERVER_PORT \
  -e WECHATY_TOKEN \
  wechaty/wechaty:0.56
