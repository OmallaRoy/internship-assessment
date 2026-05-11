from typing import List


def collatz(n: int) -> List[int]:
       
       # Handle case where a user enters a negative integer or decimal
       if type(n) is not int or n < 1:
         return "The number entered has to be a positive whole integer. "
     
    # Initialize the list to store various collections of the numbers
       integers = [n]
       
    # While loop that repeats provided that the  integer(n)  is not equal to  1
       while n != 1:
           
           # Condition(if-else) to check if the integer is odd or even.
           if n % 2 == 0:
               n = n // 2 # if the n is even,then divide it by 2
           else:
               n = n * 3 + 1 # if n is odd,then multiply by 3 and add by 1
               
           integers.append(n)
       
       return integers 

    
               
          
           
      


def distinct_numbers(numbers: List[int]) -> int:
    """
    You are given a list of integers (the list could be empty), calculate the number of distinct/unique values in the list.

    E.g if numbers = [2, 3, 2, 2, 3], then the answer is 2 since there are only 2 unique numbers: 2 and 3.
    """
    pass
