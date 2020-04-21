class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        if len(s) > 1:
            first_letter = s[0]
            find_list = [first_letter]
            length_list = []
            i = 1
            while i < len(s):
                if s[i] not in find_list:
                    find_list.append(s[i])
                else:
                    find_list.append(s[i])
                    repeat_index = find_list.index(s[i])
                    find_list_left = find_list[0:repeat_index]
                    find_list_right = find_list[repeat_index+1:]
                    find_list = find_list_right
                    length_list.append(len(find_list_left))
                length_list.append(len(find_list))
                i += 1
            return max(length_list)
        else:
            return len(s)


class Solution_1:
    def lengthOfLongestSubstring(self, s):
        """
        :type s: str
        :rtype: int
        """
        st = {}
        i, ans = 0, 0
        for j in range(len(s)):
            if s[j] in st:
                i = max(st[s[j]], i)
            ans = max(ans, j - i + 1)
            st[s[j]] = j + 1
        return ans


s = 'qewreytoafdjgf'
A = Solution_1()
result = A.lengthOfLongestSubstring(s)
print(result)

