import heapq
from core.rules import Rules
from search.search_algorithm import SearchAlgorithm

def tim_duong(st_dich, truoc_do):
    duong = []
    ht = st_dich
    while ht in truoc_do:
        truoc, hd = truoc_do[ht]
        duong.append(hd)
        ht = truoc
    duong.reverse()
    return duong

def khoang_cach(p1, p2):
    return max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))

class AStar(SearchAlgorithm):
    def heuristic(self, st, board):
        sai = list(set(st.boxes) - board.goals)
        trong = list(board.goals - set(st.boxes))
        tong = 0
        for b in sai:
            tot = min((khoang_cach(b, g) for g in trong), default=0)
            tong += tot
        return tong

    def search(self, st_dau, board, timeout_seconds=30.0):
        import time
        t_bat_dau = time.time()
        hd = []
        dem = 0
        so_node = 0
        max_hd = 1

        g = {st_dau: 0}
        h = self.heuristic(st_dau, board)
        heapq.heappush(hd, (g[st_dau] + h, dem, st_dau))
        da_xet = set()
        truoc_do = {}

        st_tot_nhat = st_dau
        h_tot_nhat = h

        while hd:
            if time.time() - t_bat_dau > timeout_seconds:
                if st_tot_nhat != st_dau:
                    return tim_duong(st_tot_nhat, truoc_do), g.get(st_tot_nhat, 0), so_node, max_hd
                return None, 0, so_node, max_hd

            f, _, st = heapq.heappop(hd)

            if st.is_goal(board):
                duong = tim_duong(st, truoc_do)
                return duong, g[st], so_node, max_hd

            if st in da_xet:
                continue
            da_xet.add(st)
            so_node += 1

            for hdg, st_tiep in Rules.get_successors(st, board):
                g_moi = g[st] + 1
                if st_tiep not in da_xet and (st_tiep not in g or g_moi < g[st_tiep]):
                    truoc_do[st_tiep] = (st, hdg)
                    g[st_tiep] = g_moi
                    h_moi = self.heuristic(st_tiep, board)
                    
                    if h_moi < h_tot_nhat:
                        h_tot_nhat = h_moi
                        st_tot_nhat = st_tiep
                        
                    dem += 1
                    heapq.heappush(hd, (g_moi + h_moi, dem, st_tiep))
                    max_hd = max(max_hd, len(hd))

        return None, 0, so_node, max_hd