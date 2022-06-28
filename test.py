input_quantity = 0
prompt = "Enter the new quantity for the item selected: "
while input_quantity <= 0:
    try:
        input_quantity = int(input(prompt))
    except Exception as e:
        pass
    if input_quantity <= 0:
        print('The quantity must be greater than 0')