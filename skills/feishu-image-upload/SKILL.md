---
name: feishu-image-upload
description: 通过飞书开放平台 API 上传图片并发送到指定用户私聊。当需要在飞书中发送截图、二维码、验证码图片等时使用。
---

# 飞书 API 图片上传与发送

## 适用场景
- `send_message` 不支持图片附件时
- 需要发送截图/二维码/验证码给用户
- 任何需要向飞书用户私聊发送图片的场景

## 前置条件

需要飞书自建应用的凭证：
- `app_id`: 应用 ID
- `app_secret`: 应用密钥
- 目标用户的 `open_id`
- 应用需已开通 **获取用户信息**、**发送消息** 权限

## 三步流程

### 1. 获取 token

```python
import requests
resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET}
)
token = resp.json()["tenant_access_token"]
```

### 2. 上传图片

```python
with open("image.png", "rb") as f:
    resp = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/images",
        headers={"Authorization": f"Bearer {token}"},
        data={"image_type": "message"},
        files={"image": ("filename.png", f, "image/png")}
    )
image_key = resp.json()["data"]["image_key"]
```

### 3. 发送消息

```python
msg = {
    "receive_id": USER_OPEN_ID,
    "msg_type": "image",
    "content": json.dumps({"image_key": image_key})
}
requests.post(
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json=msg
)
```

## 当前项目凭证

| 字段 | 值 |
|------|-----|
| app_id | `cli_a960a49baef99bdd` |
| app_secret | `Pl4hmtpxftzqLUYVjdkMChViSfqNdDlt` |
| 用户 open_id | `ou_1122210fb81365e5a8bb203286e96e65` |

## 注意事项

- Token 有效期 2 小时，过期需重新获取
- 图片格式支持 PNG/JPEG/GIF/BMP，大小 < 10MB
- `image_type` 必须是 `"message"`（消息用），不是 `"avatar"`
- 用户 open_id 可通过飞书管理后台 → 用户 → 查看详情获取
