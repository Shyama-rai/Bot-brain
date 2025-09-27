#code
marks = int(input("Enter marks: "))
if marks >= 90:
    grade = "A"
elif marks >= 80:
    grade = "B"
elif marks >= 70:
    grade = "C"
elif marks >= 45:
    grade = "D"
else:
    grade = "F"

print("Grade", grade)

#output 
# input = 51
# Grade C