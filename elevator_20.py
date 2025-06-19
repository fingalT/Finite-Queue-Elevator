import json
import datetime
from typing import List, Dict

def load_people_data(filename: str = 'people_data.json') -> List[Dict]:
    """从JSON文件加载人员数据"""
    with open(filename, 'r', encoding='utf-8') as f:
        people_data = json.load(f)
    
    # 转换字符串回datetime对象
    people = []
    for person in people_data:
        people.append({
            'id': person['id'],
            'arrival_time': datetime.datetime.fromisoformat(person['arrival_time']),
            'seconds': person['seconds']
        })
    
    return people

def process_elevator(people: List[Dict], elevator_capacity: int, elevator_time: int, max_wait_time: int = 1200):
    """处理电梯运行"""
    results = []
    waiting_times = []
    long_wait_count = 0
    abandoned_count = 0  # 因等待超时放弃的人数
    abandoned_people = []  # 记录放弃人员的详细信息
    max_queue_size = 0  # 初始化最大排队人数
    
    # 从第5分钟开始，每5分钟一班
    current_time = 300  # 5分钟 = 300秒
    batch_number = 1  # 当前班次号
    
    # 按照人员编号排序，而不是按照到达时间
    sorted_people = sorted(people, key=lambda x: x['id'])
    person_index = 0
    
    while person_index < len(sorted_people):
        # 先移除等待超时的人员
        while (person_index < len(sorted_people) and 
               sorted_people[person_index]['seconds'] <= current_time):
            person = sorted_people[person_index]
            waiting_time = current_time - person['seconds']
            
            # 如果等待时间超过最大等待时间，则放弃乘坐
            if waiting_time > max_wait_time:
                abandoned_count += 1
                abandoned_people.append({
                    'person_id': person['id'],
                    'arrival_time': person['arrival_time'],
                    'abandon_time': datetime.datetime(2024, 1, 1) + datetime.timedelta(seconds=current_time),
                    'waiting_time': waiting_time,
                    'batch_number': batch_number
                })
                person_index += 1
                continue
            else:
                break
        
        # 计算当前时刻排队人数（不包括已放弃的人员）
        queue_size = 0
        for i in range(person_index, len(sorted_people)):
            if sorted_people[i]['seconds'] <= current_time:
                waiting_time_check = current_time - sorted_people[i]['seconds']
                if waiting_time_check <= max_wait_time:
                    queue_size += 1
                else:
                    break
            else:
                break
        
        # 更新最大排队人数
        max_queue_size = max(max_queue_size, queue_size)
        
        # 确定这一班能搭载的乘客
        current_batch = []
        while (person_index < len(sorted_people) and 
               sorted_people[person_index]['seconds'] <= current_time and 
               len(current_batch) < elevator_capacity):
            person = sorted_people[person_index]
            waiting_time = current_time - person['seconds']
            
            # 再次检查是否超时（防止在循环中超时）
            if waiting_time > max_wait_time:
                abandoned_count += 1
                abandoned_people.append({
                    'person_id': person['id'],
                    'arrival_time': person['arrival_time'],
                    'abandon_time': datetime.datetime(2024, 1, 1) + datetime.timedelta(seconds=current_time),
                    'waiting_time': waiting_time,
                    'batch_number': batch_number
                })
                person_index += 1
                continue
            
            waiting_times.append(waiting_time)
            
            if waiting_time > 1200:  # 20分钟 = 1200秒
                long_wait_count += 1
                
            current_batch.append({
                'person_id': person['id'],
                'arrival_time': person['arrival_time'],
                'departure_time': datetime.datetime(2024, 1, 1) + datetime.timedelta(seconds=current_time),
                'waiting_time': waiting_time
            })
            person_index += 1
        
        if current_batch:  # 如果有人等待，即使不满员也发车
            results.append({
                'batch': batch_number,
                'passengers': current_batch
            })
        
        batch_number += 1  # 班次号递增
        current_time += 300  # 5分钟后发下一班
    
    return results, waiting_times, long_wait_count, max_queue_size, abandoned_count, abandoned_people

def save_results(results: List[Dict], waiting_times: List[float], long_wait_count: int, total_people: int, max_queue_size: int, abandoned_count: int = 0, abandoned_people: List[Dict] = None, output_file: str = 'result.txt'):
    """保存电梯运行结果"""
    if abandoned_people is None:
        abandoned_people = []
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # 写入详细记录
        batch_index = 0
        abandoned_index = 0
        
        # 获取所有班次号（包括有乘客的和只有放弃人员的）
        all_batches = set()
        for batch in results:
            all_batches.add(batch['batch'])
        for abandoned in abandoned_people:
            all_batches.add(abandoned['batch_number'])
        
        # 按班次号排序输出
        for batch_num in sorted(all_batches):
            f.write(f"\n第{batch_num}班次：\n")
            
            # 输出该班次的乘客
            batch_found = False
            for batch in results:
                if batch['batch'] == batch_num:
                    batch_found = True
                    for passenger in batch['passengers']:
                        f.write(f"骑手{passenger['person_id']}，")
                        f.write(f"到达时间：{passenger['arrival_time'].strftime('%H:%M:%S')}，")
                        f.write(f"发车时间：{passenger['departure_time'].strftime('%H:%M:%S')}，")
                        f.write(f"等待时间：{int(passenger['waiting_time'])}秒\n")
                    break
            
            # 输出该班次放弃的人员
            for abandoned in abandoned_people:
                if abandoned['batch_number'] == batch_num:
                    f.write(f"【放弃】骑手{abandoned['person_id']}，")
                    f.write(f"到达时间：{abandoned['arrival_time'].strftime('%H:%M:%S')}，")
                    f.write(f"放弃时间：{abandoned['abandon_time'].strftime('%H:%M:%S')}，")
                    f.write(f"等待时间：{int(abandoned['waiting_time'])}秒\n")
            
            # 如果该班次既没有乘客也没有放弃人员，说明是空班次
            if not batch_found and not any(a['batch_number'] == batch_num for a in abandoned_people):
                f.write("无人等待\n")
        
        # 写入统计数据
        f.write("\n统计数据：\n")
        f.write(f"电梯总运行时间：{len(results) * 5}分钟\n")
        f.write(f"电梯总服务人数：{sum(len(batch['passengers']) for batch in results)}人\n")
        f.write(f"因等待超时离开的人数：{abandoned_count}人\n")
        if waiting_times:  # 防止除零错误
            f.write(f"平均等待时间：{int(sum(waiting_times) / len(waiting_times))}秒\n")
            f.write(f"最大等待时间：{int(max(waiting_times))}秒\n")
            f.write(f"最小等待时间：{int(min(waiting_times))}秒\n")
        else:
            f.write("平均等待时间：0秒\n")
            f.write("最大等待时间：0秒\n")
            f.write("最小等待时间：0秒\n")
        f.write(f"最大排队人数：{max_queue_size}人\n")
        f.write(f"等待超过20分钟的人数比例：{(long_wait_count / total_people) * 100:.2f}%\n")

def main():
    """主函数 - 电梯运行模拟"""
    try:
        # 读取配置文件
        with open('input.json', 'r') as f:
            data = json.load(f)
        
        elevator_capacity = data['elevator_capacity']
        elevator_time = data['elevator_time']
        max_wait_time = data.get('max_wait_time', 1200)  # 默认20分钟=1200秒
        output_file = data.get('output_file', 'result.txt')  # 默认输出文件名
        
        # 获取人员数据文件名
        people_avg_arrive = data.get('people_avg_arrive', 'people_avg_arrive.txt')
        json_filename = people_avg_arrive.replace('.txt', '.json')
        
        # 加载人员数据
        people = load_people_data(json_filename)
        
        print(f"加载了 {len(people)} 名人员数据")
        print(f"人员数据文件：{json_filename}")
        print(f"电梯容量：{elevator_capacity}人")
        print(f"电梯运行间隔：{elevator_time}分钟")
        print(f"最大等待时间：{max_wait_time//60}分钟")
        print(f"输出文件：{output_file}")
        
        # 处理电梯运行
        results, waiting_times, long_wait_count, max_queue_size, abandoned_count, abandoned_people = process_elevator(
            people, elevator_capacity, elevator_time, max_wait_time)
        
        # 保存结果
        save_results(results, waiting_times, long_wait_count, len(people), max_queue_size, abandoned_count, abandoned_people, output_file)
        
        print(f"\n模拟完成！")
        print(f"总共运行 {len(results)} 班次")
        print(f"服务 {sum(len(batch['passengers']) for batch in results)} 名乘客")
        print(f"因等待超时离开 {abandoned_count} 名乘客")
        print(f"结果已保存到 {output_file}")
        
    except FileNotFoundError as e:
        print(f"文件未找到：{e}")
        print("请确保以下文件存在：")
        print("- input.json (配置文件)")
        print("- 对应的人员数据JSON文件 (由 people_arrive.py 生成)")
    except Exception as e:
        print(f"运行出错：{e}")

if __name__ == '__main__':
    main()