from hotstorage.hotstorage_model_pb2 import World, CraneSchedule, CraneMove
import math

#out = open('data.txt', 'w')

def except_target_priority(world, source_buf, except_block, except_buf):
    list = []
    for buf in world.Buffers:
        check = 0
        if buf == source_buf:
            continue
        if buf == except_buf:
            check = 1
        if len(buf.BottomToTop) - check < buf.MaxHeight:
            if len(buf.BottomToTop) > check:
                if check == 1:
                    blockList = []
                    for block in buf.BottomToTop:
                        if block == except_block:
                            continue
                        blockList.append(block)
                    block = min(blockList, key=lambda block: block.Due.MilliSeconds)
                else:
                    block = min(buf.BottomToTop, key=lambda block: block.Due.MilliSeconds)
                list.append([block.Ready, block.Due.MilliSeconds, block, buf])
            else:
                list.append([False, math.inf, None, buf])
    if list:
        list.sort(key=lambda x : -x[1])
        return list[0][3].Id
    else:
        return source_buf.Id

def target_priority(world, source_buf):
    list = []
    for buf in world.Buffers:
        if buf == source_buf:
            continue
        if len(buf.BottomToTop) < buf.MaxHeight:
            if buf.BottomToTop:
                block = min(buf.BottomToTop, key=lambda block: block.Due.MilliSeconds)
                list.append([block.Ready, block.Due.MilliSeconds, block, buf])
            else:
                list.append([False, math.inf, None, buf])
    if list:
        list.sort(key=lambda x : -x[1])
        return list[0][3].Id
    else:
        return source_buf.Id

def source_priority(world):
    list = []
    for buf in world.Buffers:
        if len(buf.BottomToTop) > 0:
            if buf.BottomToTop:
                block = min(buf.BottomToTop, key=lambda block: block.Due.MilliSeconds)
                list.append([block, buf])
    list.sort(key=lambda x : x[0].Due.MilliSeconds)
    if len(list) == len(world.Buffers):
        del list[len(list) - 1]
    return list

def top_priority(world):
    list = []
    for buf in world.Buffers:
        if len(buf.BottomToTop) > 0:
            block = buf.BottomToTop[-1]
            list.append([block, buf])
    list.sort(key=lambda x : (-x[0].Ready, x[0].Due.MilliSeconds))
    return list[0][0], list[0][1]

def ready_priority(world):
    list = []
    for buf in world.Buffers:
        if buf.BottomToTop:
            for block in buf.BottomToTop:
                if block.Ready:
                    list.append([block, buf])
    list.sort(key=lambda x : (-x[0].Ready, x[0].Due.MilliSeconds))
    return list

def total_block(world):
    list = []
    for buf in world.Buffers:
        if len(buf.BottomToTop) > 0:
            for block in buf.BottomToTop:
                list.append([block, buf])
    list.sort(key=lambda x : (-x[0].Ready, x[0].Due.MilliSeconds))
    return list

def temp_buf(world):
    list = []
    for buf in world.Buffers:
        if len(buf.BottomToTop) > 0:
            for block in buf.BottomToTop:
                list[buf.Id].append(block)
    return list

def check_block_percentage(world, check_percentage):
    buf_count = 0
    buf_total_count = 0
    for buf in world.Buffers:
        buf_total_count += buf.MaxHeight
        buf_count += len(buf.BottomToTop)
    if buf_count / buf_total_count > check_percentage:    
        return True
    else:
        return False

def check_empty_block_space(world):
    block_list = total_block(world)
    block_space = 0
    for buf in world.Buffers:
        if block_list[0][1] == buf:
            continue
        else:
            print('buf', buf.Id, len(buf.BottomToTop))
            block_space += (buf.MaxHeight - len(buf.BottomToTop))

    above_count = 0
    min_time = float('inf')
    min_time_index = -1
    for index , block in enumerate(block_list[0][1].BottomToTop):
        if min_time > block.Due.MilliSeconds:
            min_time = block.Due.MilliSeconds
            min_time_index = index
    print('bufwithsmall', len(block_list[0][1].BottomToTop), min_time_index)
    above_count = len(block_list[0][1].BottomToTop) - min_time_index - 1
    if world.Crane.Load:
        block_space -= 1
    print('aboveCnt', above_count)
    print('block_space', block_space)
    if block_space < above_count + 1:
        return True
    else:
        return False


def except_clear_stack_buf_id(world, clear_buf):
    buf_list = list()
    block_list = list()
    for buf in world.Buffers:
        if buf != clear_buf and len(buf.BottomToTop) != buf.BottomToTop.MaxHeight:
            buf_list.append(buf)
    for buf in buf_list:
        for block in buf.BottomToTop:
            block_list.append([block.Due.MilliSeconds, buf])
    if block_list:
        block_list.sort(key=lambda x: x[0])
    return block_list[0][1]



    
def crane_schedule(world):
    #if len(world.Crane.Schedule.Moves) > 0:
        #for mov in world.Crane.Schedule.Moves:
        #    if mov.SourceId == world.Production.Id:
        #        return None

    schedule = CraneSchedule()
    print('crane', world.Crane.Load)

    ###
    #ready_alone for ready_alone in block_list if ready_alone.Ready
    if check_empty_block_space(world):
        print('a')
        block_list = total_block(world)
        for i in range(len(block_list)):
            if block_list[i][0].Ready:
                if block_list[i][0] == block_list[i][1].BottomToTop[-1]:
                    print('b')
                    if world.Handover.Ready:
                        mov_handover = schedule.Moves.add()
                        mov_handover.BlockId = block_list[i][0].Id
                        mov_handover.SourceId = block_list[i][1].Id
                        mov_handover.TargetId = world.Handover.Id
                        return schedule
                    elif len(block_list[i][1].BottomToTop) == 1 and not world.Handover.Ready:
                        
                        return None                    
                        
                    elif len(block_list[i][1].BottomToTop) == 1:
                        mov_buffer = schedule.Moves.add()
                        mov_buffer.BlockId = block_list[i][0].Id
                        mov_buffer.SourceId = block_list[i][1].Id
                        mov_buffer.TargetId = target_priority(world, block_list[i][1])
                        return schedule
                    
                    else:
                        continue

                else:
                    aboveBlock = block_list[i][1].BottomToTop[-1]
                                        
                    if aboveBlock.Ready and world.Handover.Ready:
                        mov_handover = schedule.Moves.add()
                        mov_handover.BlockId = aboveBlock.Id
                        mov_handover.SourceId = block_list[i][1].Id
                        mov_handover.TargetId = world.Handover.Id
                        return schedule
                    else:
                        # single ready to handover
                        for buf in world.Buffers:
                            if len(buf.BottomToTop) == 1 and buf.BottomToTop[0].Ready:
                                mov_handover = schedule.Moves.add()
                                mov_handover.BlockId = buf.BottomToTop[0].Id
                                mov_handover.SourceId = buf.Id
                                mov_handover.TargetId = world.Handover.Id

                                return schedule


                        mov_buffer = schedule.Moves.add()
                        mov_buffer.BlockId = aboveBlock.Id
                        mov_buffer.SourceId = block_list[i][1].Id
                        mov_buffer.TargetId = target_priority(world, block_list[i][1])
                        return schedule
    for buf in world.Buffers:
        print('t')
        if len(buf.BottomToTop) == 1 and buf.BottomToTop[0].Ready:
            if len(world.Production.BottomToTop) == world.Production.MaxHeight:
                    arrival_block = world.Production.BottomToTop[-1]               
                    if world.Handover.Ready:                        
                        mov_handover = schedule.Moves.add()
                        mov_handover.BlockId = buf.BottomToTop[0].Id
                        mov_handover.SourceId = buf.Id
                        mov_handover.TargetId = world.Handover.Id

                        mov_buffer = schedule.Moves.add()
                        mov_buffer.BlockId = arrival_block.Id
                        mov_buffer.SourceId = world.Production.Id
                        mov_buffer.TargetId = except_target_priority(world, world.Production, buf.BottomToTop[0].Id, buf)
                        

                        return schedule

                    else:
                        mov_handover = schedule.Moves.add()
                        mov_handover.BlockId = buf.BottomToTop[0].Id
                        mov_handover.SourceId = buf.Id
                        mov_handover.TargetId = target_priority(world, buf)
                        return schedule


            else:
                if world.Handover.Ready:                        
                    mov_handover = schedule.Moves.add()
                    mov_handover.BlockId = buf.BottomToTop[0].Id
                    mov_handover.SourceId = buf.Id
                    mov_handover.TargetId = world.Handover.Id

                    return schedule

                else:
                    mov_handover = schedule.Moves.add()
                    mov_handover.BlockId = buf.BottomToTop[0].Id
                    mov_handover.SourceId = buf.Id
                    mov_handover.TargetId = target_priority(world, buf)

                    return schedule                                    
        ###


    top_block, top_block_buf = top_priority(world)
    
    if len(world.Production.BottomToTop) == world.Production.MaxHeight:
        arrival_block = world.Production.BottomToTop[-1]
        print('k')
        
        if top_block.Ready and world.Handover.Ready:
            mov_handover = schedule.Moves.add()
            mov_handover.BlockId = top_block.Id
            mov_handover.SourceId = top_block_buf.Id
            mov_handover.TargetId = world.Handover.Id

            mov_buffer = schedule.Moves.add()
            mov_buffer.BlockId = arrival_block.Id
            mov_buffer.SourceId = world.Production.Id
            mov_buffer.TargetId = except_target_priority(world, world.Production, top_block, top_block_buf)
            return schedule

        mov = schedule.Moves.add()
        mov.BlockId = arrival_block.Id
        mov.SourceId = world.Production.Id
        mov.TargetId = target_priority(world, world.Production)
        return schedule
    
    if len(world.Crane.Schedule.Moves) > 0:
        return None

    sourceList = source_priority(world)

    for i, (block, buf) in enumerate(sourceList, start = 1):
        print('v')
        if block == buf.BottomToTop[-1]:
            if block.Ready:
                if world.Handover.Ready:
                    mov_handover = schedule.Moves.add()
                    mov_handover.BlockId = block.Id
                    mov_handover.SourceId = buf.Id
                    mov_handover.TargetId = world.Handover.Id
                    return schedule
                
                else:
                    if i == len(sourceList):
                        targetId = target_priority(world, buf)
                        if targetId == sourceList[0][1].Id:
                            break
                        mov_buffer = schedule.Moves.add()
                        mov_buffer.BlockId = block.Id
                        mov_buffer.SourceId = buf.Id
                        mov_buffer.TargetId = targetId
                        return schedule
                    
                    for j, (block2, buf2) in enumerate(sourceList, start = 1):
                        if i >= j:
                            continue

                        if block2 == buf2.BottomToTop[-1]:
                            mov_buffer = schedule.Moves.add()
                            mov_buffer.BlockId = block.Id
                            mov_buffer.SourceId = buf.Id
                            mov_buffer.TargetId = buf2.Id
                            return schedule
                        
                        else:
                            targetId = target_priority(world, buf2)
                            if targetId == sourceList[0][1].Id:
                                break
                            mov_buffer = schedule.Moves.add()
                            mov_buffer.BlockId = buf2.BottomToTop[-1].Id
                            mov_buffer.SourceId = buf2.Id
                            mov_buffer.TargetId = targetId
                            return schedule

            if len(buf.BottomToTop) == 1:
                if i == len(sourceList):
                    targetId = target_priority(world, buf)
                    if targetId == sourceList[0][1].Id:
                        break
                    mov_buffer = schedule.Moves.add()
                    mov_buffer.BlockId = block.Id
                    mov_buffer.SourceId = buf.Id
                    mov_buffer.TargetId = targetId
                    return schedule

                for j, (block2, buf2) in enumerate(sourceList, start = 1):
                    if i >= j:
                        continue

                    mov_buffer = schedule.Moves.add()
                    mov_buffer.BlockId = block.Id
                    mov_buffer.SourceId = buf.Id

                    if block2 == buf2.BottomToTop[-1]:
                        mov_buffer.TargetId = buf2.Id
                    else:
                        mov_buffer.TargetId = target_priority(world, buf)

                    return schedule

            else:
                continue
                    
        else:
            for j in range(1, len(buf.BottomToTop) + 1):
                if buf.BottomToTop[-j] == block:
                    break
                
                targetId = target_priority(world, buf)
                if targetId == sourceList[0][1].Id:
                    break

                mov_handover = schedule.Moves.add()
                mov_handover.BlockId = buf.BottomToTop[-j].Id
                mov_handover.SourceId = buf.Id
                mov_handover.TargetId = world.Handover.Id

                mov_buffer = schedule.Moves.add()
                mov_buffer.BlockId = buf.BottomToTop[-j].Id
                mov_buffer.SourceId = buf.Id
                mov_buffer.TargetId = targetId
                
            if len(schedule.Moves) > 0:
                return schedule

    ready_list = ready_priority(world)
    if ready_list:
        for block, buf in ready_list:
            for i in range(1, len(buf.BottomToTop) + 1):             
                mov_handover = schedule.Moves.add()
                mov_handover.BlockId = buf.BottomToTop[-i].Id
                mov_handover.SourceId = buf.Id
                mov_handover.TargetId = world.Handover.Id

                mov_buffer = schedule.Moves.add()
                mov_buffer.BlockId = buf.BottomToTop[-i].Id
                mov_buffer.SourceId = buf.Id
                mov_buffer.TargetId = target_priority(world, buf)

                if buf.BottomToTop[-i] == block:
                    break

            return schedule
    
    """
    block_list = total_block(world)
    for i in range(len(block_list)):
        if block_list[i][0]:
            if block_list[i][2] == block_list[i][3].BottomToTop[-1]:
                if world.Handover.Ready:
                    mov_handover = schedule.Moves.add()
                    mov_handover.BlockId = block_list[i][2].Id
                    mov_handover.SourceId = block_list[i][3].Id
                    mov_handover.TargetId = world.Handover.Id
                    return schedule

                elif len(block_list[i][3].BottomToTop) == 1:
                    mov_buffer = schedule.Moves.add()
                    mov_buffer.BlockId = block_list[i][2].Id
                    mov_buffer.SourceId = block_list[i][3].Id
                    mov_buffer.TargetId = target_priority(world, block_list[i][3])
                    return schedule

                else:
                    continue

            else:
                aboveBlock = block_list[i][3].BottomToTop[-1]
                
                if aboveBlock.Ready and world.Handover.Ready:
                    mov_handover = schedule.Moves.add()
                    mov_handover.BlockId = aboveBlock.Id
                    mov_handover.SourceId = block_list[i][3].Id
                    mov_handover.TargetId = world.Handover.Id
                    return schedule

                else:
                    mov_buffer = schedule.Moves.add()
                    mov_buffer.BlockId = aboveBlock.Id
                    mov_buffer.SourceId = block_list[i][3].Id
                    mov_buffer.TargetId = target_priority(world, block_list[i][3])
                    return schedule
        else:
            sourceList = source_priority(world)
            for block, buf in sourceList:
                if block == buf.BottomToTop[-1]:
                    if len(buf.BottomToTop) == 1:
                        mov_buffer = schedule.Moves.add()
                        mov_buffer.BlockId = block.Id
                        mov_buffer.SourceId = buf.Id
                        mov_buffer.TargetId = target_priority(world, buf)
                        return schedule
                    else:
                        continue
                    
                mov_buffer = schedule.Moves.add()
                mov_buffer.BlockId = buf.BottomToTop[-1].Id
                mov_buffer.SourceId = buf.Id
                mov_buffer.TargetId = target_priority(world, buf)
                return schedule
        """
    return None
