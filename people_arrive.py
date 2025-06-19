import random
import datetime
import json
from typing import List, Dict

def generate_arrival_times(hourly_people: List[int]) -> List[Dict]:
    """生成人员到达时间"""
    people = []
    person_id = 1
    
    # 按小时处理人员到达
    for hour, count in enumerate(hourly_people):
        # 为每小时的人员生成均匀分布的到达时间
        arrival_times = []
        for _ in range(count):
            # 生成该小时内的随机秒数
            seconds = random.uniform(0, 3600)
            # 计算总秒数
            total_seconds = hour * 3600 + seconds
            # 转换为时间格式
            arrival_time = datetime.datetime(2024, 1, 1, hour, 0, 0) + datetime.timedelta(seconds=seconds)
            
            arrival_times.append((arrival_time, total_seconds))
        
        # 按到达时间排序
        arrival_times.sort(key=lambda x: x[1])
        
        # 分配编号
        for arrival_time, total_seconds in arrival_times:
            people.append({
                'id': person_id,
                'arrival_time': arrival_time,
                'seconds': total_seconds
            })
            person_id += 1
    
    # 按到达时间排序
    return sorted(people, key=lambda x: x['seconds'])

def save_people_file(people: List[Dict], filename: str = 'people.txt'):
    """保存人员到达时间文件"""
    # 按照人员编号排序
    sorted_people = sorted(people, key=lambda x: x['id'])
    with open(filename, 'w', encoding='utf-8') as f:
        for person in sorted_people:
            f.write(f"骑手{person['id']}，到达时间：{person['arrival_time'].strftime('%H:%M:%S')}\n")

def save_people_data(people: List[Dict], filename: str = 'people_data.json'):
    """保存人员数据为JSON格式，供电梯模拟使用"""
    # 转换datetime对象为字符串
    people_data = []
    for person in people:
        people_data.append({
            'id': person['id'],
            'arrival_time': person['arrival_time'].isoformat(),
            'seconds': person['seconds']
        })
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(people_data, f, ensure_ascii=False, indent=2)

def main():
    """主函数 - 生成人员到达时间"""
    # 读取输入文件
    with open('input.json', 'r') as f:
        data = json.load(f)
    
    hourly_people = data['hourly_people']
    people_avg_arrive = data.get('people_avg_arrive', 'people_avg_arrive.txt')
    
    # 生成人员到达时间
    people = generate_arrival_times(hourly_people)
    
    # 保存人员到达时间文件
    save_people_file(people, people_avg_arrive)
    
    # 保存人员数据为JSON格式
    json_filename = people_avg_arrive.replace('.txt', '.json')
    save_people_data(people, json_filename)
    
    print(f"已生成 {len(people)} 名人员的到达时间")
    print("文件已保存：")
    print(f"- {people_avg_arrive} (可读格式)")
    print(f"- {json_filename} (数据格式)")

if __name__ == '__main__':
    main()