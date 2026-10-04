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

class UCS(SearchAlgorithm):
    def search(self, st_dau, board, timeout_seconds=30.0):
        import time
        t_bat_dau = time.time()
        hd = []
        dem = 0
        so_node = 0
        max_hd = 1

        heapq.heappush(hd, (0, dem, st_dau))
        da_xet = set()
        truoc_do = {}
        chi_phi = {st_dau: 0}

        st_tot_nhat = st_dau
        
        def ham_h_phu(st):
            sai = list(set(st.boxes) - board.goals)
            trong = list(board.goals - set(st.boxes))
            t = 0
            for b in sai:
                tot = min((max(abs(b[0] - g[0]), abs(b[1] - g[1])) for g in trong), default=0)
                t += tot
            if sai:
                toi_hop = min(max(abs(st.agent_pos[0] - b[0]), abs(st.agent_pos[1] - b[1])) for b in sai)
                t += toi_hop
            return t
            
        h_tot_nhat = ham_h_phu(st_dau)

        while hd:
            if time.time() - t_bat_dau > timeout_seconds:
                if st_tot_nhat != st_dau:
                    return tim_duong(st_tot_nhat, truoc_do), chi_phi.get(st_tot_nhat, 0), so_node, max_hd
                return None, 0, so_node, max_hd

            g, _, st = heapq.heappop(hd)

            if st in da_xet:
                continue
            da_xet.add(st)
            so_node += 1

            if st.is_goal(board):
                duong = tim_duong(st, truoc_do)
                return duong, g, so_node, max_hd

            for hdg, st_tiep in Rules.get_successors(st, board):
                g_moi = g + 1
                if st_tiep not in da_xet and (st_tiep not in chi_phi or g_moi < chi_phi[st_tiep]):
                    chi_phi[st_tiep] = g_moi
                    truoc_do[st_tiep] = (st, hdg)
                    
                    h_tam = ham_h_phu(st_tiep)
                    if h_tam < h_tot_nhat:
                        h_tot_nhat = h_tam
                        st_tot_nhat = st_tiep
                        
                    dem += 1
                    heapq.heappush(hd, (g_moi, dem, st_tiep))

            max_hd = max(max_hd, len(hd))

        return None, 0, so_node, max_hd