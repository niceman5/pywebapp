'''
팰린드롬이랑 앞으로 해도 뒤로 해도 동일한 문자열
'''

# list의 처음과 마지막을 비교해 가면서 체크
def check1(str1):
    # print(len(str1))
    max_loop = len(str1) / 2
    for i in range(0, int(max_loop)):
        # print('{0}'.format(i))
        if str1[i] != str1[(len(str1)-1)-i]:
            return False
    return True

if __name__ == '__main__':
    str1 = '1AE  DCBA1'
    str_new = []

    # 문자열에 숫자와 문자만 남긴다.
    for char in str1:
        if char.isalnum():
            str_new.append(char)

    print('str_new = {}'.format(str_new))
    print('check1={0} 결과 {1}'.format(str_new, check1(str_new)))
