# 电梯模拟系统
### 1. people_arrive.py - 人员生成模块
- **功能**：根据配置生成人员到达时间
- **输入**：`input.json` 配置文件
- **输出**：
  - `people.txt` - 可读格式的人员到达时间
  - `people_data.json` - 供电梯模拟使用的数据文件

### 2. elevator_20.py - 电梯运行模拟模块
- **功能**：模拟电梯运行，处理人员排队和等待
- **输入**：
  - `input.json` - 配置文件（电梯容量、运行间隔等）
  - `people_data.json` - 人员数据文件
- **输出**：`result.txt` - 电梯运行结果和统计数据

## 使用方法
1. **生成人员数据**：
   ```bash
   python people_arrive.py
   ```
2. **运行电梯模拟**：
   ```bash
   python elevator_20.py
   ```

## 配置文件格式
`input.json` 示例：
```json
{
  "hourly_people": [247, 700, 333, 206],
  "elevator_capacity": 20,
  "elevator_time": 5
}
```

- `hourly_people`: 每小时到达的人数数组
- `elevator_capacity`: 电梯容量
- `elevator_time`: 电梯运行间隔

## 输出文件说明
### people.txt
可读格式的人员到达时间：
```
骑手1，到达时间：00:15:30
骑手2，到达时间：00:25:45
...
```

### people_data.json
JSON格式的人员数据，供电梯模拟使用：
```json
[
  {
    "id": 1,
    "arrival_time": "2024-01-01T00:15:30",
    "seconds": 930
  },
  ...
]
```

### result.txt
电梯运行结果和统计数据：
- 每班次的详细运行记录
- 统计数据（平均等待时间、最大排队人数等）
