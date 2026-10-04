from collections import deque
from core.rules import Rules
from search.search_algorithm import SearchAlgorithm

def tim_duong(st_dich, truoc_do):
    duong_di = []
    hien_tai = st_dich
    while hien_tai in truoc_do:
        truoc, hanh_dong = truoc_do[hien_tai]
        duong_di.append(hanh_dong)
        hien_tai = truoc
    duong_di.reverse()
    return duong_di

class BFS(SearchAlgorithm):
    def search(self, st_dau, board, timeout_seconds=30.0):
        import time
        t_bat_dau = time.time()
        hd = deque()
        da_xet = set()
        truoc_do = {}
        so_node = 0
        max_hd = 1

        hd.append(st_dau)
        da_xet.add(st_dau)

        while hd:
            if time.time() - t_bat_dau > timeout_seconds:
                return None, 0, so_node, max_hd

            st = hd.popleft()
            so_node += 1

            if st.is_goal(board):
                duong = tim_duong(st, truoc_do)
                return duong, len(duong), so_node, max_hd

            for hdg, st_tiep in Rules.get_successors(st, board):
                if st_tiep not in da_xet:
                    da_xet.add(st_tiep)
                    truoc_do[st_tiep] = (st, hdg)
                    hd.append(st_tiep)

            max_hd = max(max_hd, len(hd))

        return None, 0, so_node, max_hd