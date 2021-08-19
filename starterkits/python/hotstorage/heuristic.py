from hotstorage.hotstorage_model_pb2 import World, CraneSchedule, CraneMove

def crane_schedule(world):
    if len(world.Crane.Schedule.Moves) > 0:
        return None
    schedule = CraneSchedule()
    if len(world.Production.BottomToTop) > 0 and str(world.Now) != '':
        for blk in world.Production.BottomToTop:
            if int(str(blk.Due).split(' ')[1]) - int(str(world.Now).split(' ')[1]) < 120000:
                block = world.Production.BottomToTop[-1]
                min_time_list = list()
                for buf in world.Buffers:
                    min_time = 9999999999
                    bottom_to_top = buf.BottomToTop
                    for each_block in bottom_to_top:
                        if min_time > int(str(each_block.Due).split(':')[1]):
                            min_time = int(str(each_block.Due).split(':')[1])
                    min_time_list.append([buf, min_time])
                min_time_list.sort(key=lambda x: x[1]) # time sort
                min_time_list.reverse()
                for buf_with_time in min_time_list:
                    if buf_with_time[0].MaxHeight > len(buf_with_time[0].BottomToTop):
                        mov = schedule.Moves.add()
                        mov.BlockId = block.Id
                        mov.SourceId = world.Production.Id
                        mov.TargetId = buf_with_time[0].Id
                        return schedule
    if len(world.Production.BottomToTop) > world.Production.MaxHeight - 2:
        block = world.Production.BottomToTop[-1]
        min_time_list = list()
        for buf in world.Buffers:
            min_time = 9999999999
            bottom_to_top = buf.BottomToTop
            for each_block in bottom_to_top:
                if min_time > int(str(each_block.Due).split(':')[1]):
                    min_time = int(str(each_block.Due).split(':')[1])
            min_time_list.append([buf, min_time])
        min_time_list.sort(key=lambda x: x[1]) # time sort
        min_time_list.reverse()
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