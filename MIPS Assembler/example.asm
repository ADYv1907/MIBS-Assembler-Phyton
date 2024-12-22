.text
again: add $11, $12, $23
show:  addi $8, $7, -1234
       andi $3, $7, 127
       beq $8, $10, show
       bne $4, $6, x1
x1:    sll $17, $18, 4
       j again
