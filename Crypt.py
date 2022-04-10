import numpy as np

# from random import choice
# from math import ceil

# class CipherOfColumnarTransposition:
#     def CipherOfColumnarTransposition_Encryption(self, length_line: int, text: str):
#         encrypted_text = ""
#         list_of_parts = []
#         for i in range(length_line):
#             list_of_parts.append("")
    
#         for i in range(len(text)):
#             new_i = i
#             while new_i > (length_line-1):
#                 new_i -= length_line
#             list_of_parts[new_i] += text[i]
    
#         length_columns = ceil(len(text)/length_line)
#         for partOfList in list_of_parts:
#             while len(partOfList) != length_columns:
#                 partOfList += " "
#             encrypted_text += partOfList
#         return encrypted_text

#     def CipherOfColumnarTransposition_Decryption(self, length_line: int, encrypted_text: str):
#         decrypted_text = ""
#         list_of_parts = []
#         for i in range(length_line):
#             list_of_parts.append("")

#         length_columns = ceil(len(encrypted_text)/length_line)
#         firstI_ofPart = 0
#         numberPartOfList = -1
#         for i in range(len(encrypted_text)+1):
#             if i % length_columns == 0:
#                 list_of_parts[numberPartOfList] = encrypted_text[firstI_ofPart:i]
#                 numberPartOfList += 1
#                 firstI_ofPart = i

#         for j in range(length_columns):
#             for i in range(len(list_of_parts)):
#                 decrypted_text += (list_of_parts[i])[j]
#         return decrypted_text

#       def Reverse(self, text: str):
#             return text[::-1]

class RSA:
    primeNumbers_array = np.array
    public_key = (0, 0)
    private_key = (0, 0)

    def __init__(self):
        self.GetPrimeNumbers(50000)
        # with open("prime_numbers.txt", "w") as file:
        #     file.write("\n".join(map(str, self.primeNumbers_array)))

        # with open("prime_numbers.txt", "r") as file:
        #     text = file.read()
        #     self.primeNumbers_array = np.array(list(map(int, text.split("\n"))))

    def GetPrimeNumbers(self, maxNumber: int):
        """Находит простые числа от 2 до maxNumber (алгоритм решето Эратосфена)."""
        primeNumbers_list = list()
        sieve = [True] *  maxNumber
        for i in range(3,int(maxNumber**0.5)+1,2):
            if sieve[i]:
                sieve[i*i::2*i]=[False]*((maxNumber-i*i-1)//(2*i)+1)
        primeNumbers_list.append(2)
        for i in range(3, maxNumber, 2):
            if sieve[i]:
                primeNumbers_list.append(i)
        self.primeNumbers_array = np.array(primeNumbers_list)

    def FindMaxID(self, text: str):
        """Находит максимальный id из text по таблице юникода."""
        maxId = 0
        for i in text:
            if ord(i) > maxId:
                maxId = ord(i)
        return maxId

    def FindMultipliers(self, number: int):
        """Находит все простые множители числа."""
        i = 2
        numbers = []
        while i * i <= number:
            while number % i == 0:
                numbers.append(i)
                number = number / i
            i += 1
        if number > 1:
            numbers.append(number)
        return list(set(numbers))

    def Find_e(self, f):
        """Находит e по 2 правилам:
        1) e < f
        2) e взаимно простое с f"""

        list_of_unnecessary_items = self.FindMultipliers(f)
        while True:
            e = np.random.choice(self.primeNumbers_array)
            if e not in list_of_unnecessary_items and e < f:
                break
        
        return e

    def Find_d(self, e, f):
        k = 0
        while True:
            k += 1
            d = (k * f + 1) / e
            if d % 1 == 0:
                if d < 0:
                    print("error!!!")
                break
        return int(d)

    def GenerateKeys(self, maxId: int):
        "Генерирует открытый (public_key) и закрытый (private_key) ключи."
        while True:
            while True:
                p = np.random.choice(self.primeNumbers_array)
                q = np.random.choice(self.primeNumbers_array)
                if p != q:
                    break
            n = np.uint32(p) * np.uint32(q)
            if maxId < n:
                break
        f = np.uint32(p - 1) * np.uint32(q - 1)
        e = self.Find_e(f)
        d = self.Find_d(e, f)

        self.public_key = (e, n)
        self.private_key = (d, n)

    def Encryption_RSA(self, text: str, public_key: tuple):
        if public_key == (0, 0):
            raise ValueError("Keys not generated!!!")
        encrypted_text = list()

        for symbol in text:
            encrypted_text.append((pow(
                (ord(symbol)),
                int(public_key[0]),
                int(public_key[1])
                )))

        return " ".join(map(str, encrypted_text))

    def Decryption_RSA(self, encrypted_text_list: list):
        if self.public_key == (0, 0) or self.private_key == (0, 0):
            raise ValueError("Keys not generated!!!")
        decrypted_text = ""

        for symbol in encrypted_text_list:
            a = pow(
                int(symbol),
                int(self.private_key[0]), 
                int(self.private_key[1])
                )
            decrypted_text += chr(a)

        return decrypted_text

class Crypt(RSA):
    def __init__(self):
        super().__init__()

    def Encryption(self, text: str, public_key: tuple):
        encrypted_text = self.Encryption_RSA(text, public_key)
        return encrypted_text

    def Decryption(self, encrypted_text: str):
        decrypted_text = self.Decryption_RSA(list(map(int, encrypted_text.split(" "))))
        return decrypted_text