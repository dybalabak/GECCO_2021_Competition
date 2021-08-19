from hotstorage.hotstorage_model_pb2 import World, CraneSchedule, CraneMove
import sys

def crane_schedule(world):
    if len(world.Crane.Schedule.Moves) > 0:
        return None
    schedule = CraneSchedule()
    if len(world.Production.BottomToTop) > 0:
        block = world.Production.BottomToTop[-1]
        min_time = 9999999999
        min_time_list = list()
        for buf in world.Buffers:
            bottom_to_top = buf.BottomToTop
            for each_block in bottom_to_top:
                if min_time > int(str(each_block.Due).split(':')[1]):
                    min_time = int(str(each_block.Due).split(':')[1])
            min_time_list.append([buf, min_time])
        print('min_time_list1', min_time_list)
        min_time_list.sort(key=lambda x: x[1]) # time sort
        min_time_list.reverse()
        print('min_time_list2', min_time_list)
        for buf_with_time in min_time_list:
            if buf_with_time[0].MaxHeight > len(buf_with_time[0].BottomToTop):
                mov = schedule.Moves.add()
                mov.BlockId = block.Id
                mov.SourceId = world.Production.Id
                mov.TargetId = buf_with_time[0].Id
                return schedule
        '''
        for buf in world.Buffers:
            if buf.MaxHeight > len(buf.BottomToTop):
                mov = schedule.Moves.add()
                mov.BlockId = block.Id
                mov.SourceId = world.Production.Id
                mov.TargetId = buf.Id
                return schedule
        '''
    return None