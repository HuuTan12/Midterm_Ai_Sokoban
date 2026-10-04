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

def khoang_cach_chebyshev(p1, p2):
    return max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))

class GBFS(SearchAlgorithm):
    def heuristic(self, st, board):
        sai_vi_tri = list(set(st.boxes) - board.goals)
        dich_trong = list(board.goals - set(st.boxes))
        if not sai_vi_tri:
            return 0
        tong = 0
        for b in sai_vi_tri:
            tot_nhat = min((khoang_cach_chebyshev(b, g) for g in dich_trong), default=0)
            tong += tot_nhat
        return tong

    def search(self, st_dau, board, timeout_seconds=30.0):
        import time
        t_bat_dau = time.time()
        hang_doi = []
        dem = 0
        so_node = 0
        max_hd = 1

        h0 = self.heuristic(st_dau, board)
        heapq.heappush(hang_doi, (h0, dem, st_dau))
        da_xet = set()
        truoc_do = {}
        g_score = {st_dau: 0}

        while hang_doi:
            if time.time() - t_bat_dau > timeout_seconds:
                return None, 0, so_node, max_hd

            _, _, st = heapq.heappop(hang_doi)

            if st in da_xet:
                continue
            da_xet.add(st)
            so_node += 1

            if st.is_goal(board):
                duong = tim_duong(st, truoc_do)
                return duong, g_score.get(st, len(duong)), so_node, max_hd

            for hd, st_tiep in Rules.get_successors(st, board):
                if st_tiep in da_xet:
                    continue
                g_moi = g_score.get(st, 0) + 1
                if st_tiep not in g_score or g_moi < g_score[st_tiep]:
                    g_score[st_tiep] = g_moi
                    truoc_do[st_tiep] = (st, hd)
                    h = self.heuristic(st_tiep, board)
                    dem += 1
                    heapq.heappush(hang_doi, (h, dem, st_tiep))

            max_hd = max(max_hd, len(hang_doi))

        return None, 0, so_node, max_hd
