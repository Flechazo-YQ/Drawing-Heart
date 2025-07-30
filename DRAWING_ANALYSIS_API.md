# 绘画分析功能API文档

## 重要更新

**AI对话系统现在支持时间限制的分析参考**：
- **优先策略**：首先参考当日的绘画分析结果
- **次要策略**：如果当日无分析，则参考4小时内的最新分析
- **兜底策略**：如果都没有，则不参考任何分析结果
- 这样确保AI只基于用户最新且时效性强的心理状态进行对话

## 新增的数据表结构

### drawing_analyses 集合
存储用户的绘画分析结果，包含以下字段：

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId - 用户ID",
  "image_path": "String - 图片文件路径",
  "analysis_result": "String - AI分析结果文本",
  "analysis_date": "String - 分析日期(YYYY-MM-DD格式)",
  "created_at": "DateTime - 创建时间",
  "updated_at": "DateTime - 更新时间",
  "metadata": {
    "image_size": "String - 图片大小",
    "analysis_type": "String - 分析类型(如house_tree_person)",
    "ai_model": "String - 使用的AI模型",
    "confidence_score": "Number - 置信度分数",
    "analysis_duration": "Number - 分析耗时(秒)"
  },
  "tags": ["String"] - 分析标签数组,
  "emotional_indicators": {
    "anxiety_level": "Number - 焦虑水平(0-10)",
    "depression_level": "Number - 抑郁水平(0-10)", 
    "stress_level": "Number - 压力水平(0-10)",
    "confidence_level": "Number - 自信水平(0-10)",
    "creativity_level": "Number - 创造力水平(0-10)"
  },
  "is_active": "Boolean - 是否激活"
}
```

## 时间限制逻辑

### AI对话系统参考规则
1. **优先级1**：获取当日分析结果（00:00-23:59:59）
2. **优先级2**：如果当日无分析，获取4小时内最新分析
3. **兜底策略**：如果都无分析，不参考任何分析结果

### 时间计算说明
- **当日分析**：从当天00:00:00到23:59:59的所有分析
- **4小时内分析**：从当前时间往前推4小时的分析
- **时区处理**：所有时间均使用UTC时间进行计算

## 新增的API接口

### 1. 获取用户分析历史（增强版）
**GET** `/api/user/analyses`

**请求头:**
```
Authorization: Bearer <token>
```

**查询参数:**
- `page` (可选): 页码，默认为1
- `limit` (可选): 每页条数，默认为10

**响应示例:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "analyses": [
      {
        "_id": "...",
        "user_id": "...",
        "analysis_result": "分析结果文本...",
        "analysis_date": "2025-01-15",
        "created_at": "2025-01-15T10:30:00Z",
        "tags": ["积极", "稳定"],
        "emotional_indicators": {
          "anxiety_level": 2,
          "depression_level": 1,
          "confidence_level": 8
        }
      }
    ],
    "page": 1,
    "limit": 10,
    "total": 5
  }
}
```

### 2. 获取当日分析结果
**GET** `/api/user/today-analysis`

**请求头:**
```
Authorization: Bearer <token>
```

**响应示例:**
```json
{
  "code": 0,
  "message": "success", 
  "data": {
    "_id": "...",
    "user_id": "...",
    "analysis_result": "今日的分析结果...",
    "analysis_date": "2025-01-15",
    "created_at": "2025-01-15T10:30:00Z",
    "emotional_indicators": {
      "anxiety_level": 3,
      "confidence_level": 7
    }
  }
}
```

**无当日分析时:**
```json
{
  "code": 1,
  "message": "今日暂无分析记录"
}
```

### 3. 获取最新分析结果
**GET** `/api/user/latest-analysis`

**请求头:**
```
Authorization: Bearer <token>
```

**响应示例:**
```json
{
  "code": 0,
  "message": "success", 
  "data": {
    "_id": "...",
    "user_id": "...",
    "analysis_result": "最新的分析结果...",
    "analysis_date": "2025-01-14",
    "created_at": "2025-01-14T15:20:00Z",
    "emotional_indicators": {
      "anxiety_level": 3,
      "confidence_level": 7
    }
  }
}
```

**无分析记录时:**
```json
{
  "code": 1,
  "message": "暂无分析记录"
}
```

## AI对话功能更新

### 最新分析结果参考机制
- 当用户进行AI对话时，系统会自动检查用户最新的绘画分析结果（不限日期）
- 如果存在分析结果，AI会参考该结果进行针对性的心理咨询
- 如果不存在分析结果，AI会使用通用的心理咨询模式
- 系统消息会根据最新分析结果动态调整，提供更精准的心理支持

### 系统消息示例
**有最新分析结果时:**
```
你现在是一名心理医师，你的名字叫绘心同学。用户在[分析日期]完成了心理绘画测试，以下是最新的分析结果：[具体分析内容]

请结合这个分析结果帮助用户，用通俗易懂的语言与用户交流，用多轮对话的形式，每次别说太多。如果用户的问题与绘画分析相关，请参考分析结果给出建议。
```

**无分析结果时:**
```
你现在是一名心理医师，你的名字叫绘心同学。请用温暖、专业的语言与用户交流，用多轮对话的形式，每次别说太多。如果用户需要心理绘画分析，请引导他们先完成绘画测试。
```

## 数据库索引
为了优化查询性能，已为以下字段创建索引：
- `user_id`: 用户查询
- `analysis_date`: 日期查询
- `(user_id, analysis_date)`: 复合索引，用于查询特定用户的特定日期分析
- `created_at`: 时间排序

## 使用方法

### 后端开发者
1. 导入 `drawing_analysis_manager` 从 `mongodb_config`
2. 使用 `save_analysis()` 保存分析结果
3. 使用 `get_latest_analysis()` 获取最新分析（推荐用于AI对话）
4. 使用 `get_today_analysis()` 获取当日分析
5. 使用 `get_user_analyses()` 获取历史分析

### 前端开发者
1. 调用 `/api/user/latest-analysis` 获取最新分析（推荐用于显示用户状态）
2. 调用 `/api/user/today-analysis` 检查当日是否有分析
3. 调用 `/api/user/analyses` 获取历史分析列表
4. 在聊天界面可以提示用户最新的分析状态
