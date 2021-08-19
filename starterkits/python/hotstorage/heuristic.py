from hotstorage.hotstorage_model_pb2 import World, CraneSchedule, CraneMove

out = open('output.txt', 'w')

def crane_schedule(world):
    if len(world.Crane.Schedule.Moves) > 0:
        return None
    schedule = CraneSchedule()

    min_time_list2 = list()
    for buf in world.Buffers:
        min_time2 = 9999999999
        bottom_to_top2 = buf.BottomToTop
        emergent_Id = -1
        for each_block in bottom_to_top2:
            if min_time2 > int(str(each_block.Due).split(':')[1]):
                min_time2 = int(str(each_block.Due).split(':')[1])
                emergent_Id = each_block.Id
        min_time_list2.append([buf, min_time2, emergent_Id])
    min_time_list2.sort(key=lambda x: x[1]) # time sort
    #min_time_list2.reverse()

    for i, each_block2 in enumerate(min_time_list2[0][0].BottomToTop):
        if each_block2.Id == min_time_list2[0][2] and each_block2.Ready:
            print('each_block', each_block2, file=out)
            upper_buf_len = len(min_time_list2[0][0].BottomToTop) - i - 1
            print('upper_buf_len', upper_buf_len, file=out)
            #if world.Handover.ready:
            buf_len_list = list()
            for buf in world.Buffers:
                buf_len_list.append([buf.Id ,len(buf.BottomToTop)])
            
            buf_len_list.sort(key=lambda x: x[1])

            for i, buf in enumerate(buf_len_list):
                if buf[0] == min_time_list2[0][0].Id:
                    del buf_len_list[i]
                    break

            #while upper_buf_len > 0:
            if upper_buf_len != 0:
                mov = schedule.Moves.add()
                mov.BlockId = min_time_list2[0][0].BottomToTop[-1].Id
                mov.SourceId = min_time_list2[0][0].Id
                mov.TargetId = buf_len_list[0][0]
                return schedule
            else:
                mov = schedule.Moves.add()
                mov.BlockId = min_time_list2[0][0].BottomToTop[-1].Id
                mov.SourceId = min_time_list2[0][0].Id
                mov.TargetId = world.Handover.Id
                return schedule
        else:
            pass
    
    '''
    for buf_with_time2 in min_time_list2:
        for i, each_block2 enumerate buf_with_time2[0].BottomToTop:
            if each_block2.ready:
                upper_buf_len = len(each_block2) - i - 1
            else:
                pass
    '''
    
    if len(world.Production.BottomToTop) > 0 and str(world.Now) != '':
        for blk in world.Production.BottomToTop:
            if int(str(blk.Due).split(' ')[1]) - int(str(world.Now).split(' ')[1]) < 60000:
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