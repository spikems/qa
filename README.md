1. start server
cd chatrobot
nohup python -u manage.py runserver 192.168.241.6:10020 >log.info 2>&1 &

2.how to use ask question
example: cd test & python ask_qa.py

3.run.py is main process
3.1 if question is too short or too long  return 'The number of the word more than 50 or less than 5'

3.2 classify : distinguish  the quesiton is it a comparison class . if True return true, else return false
    input:{question:str } output :{question_type:bool}

3.3.extract :extract some keyword from database intend to understand a problem.
            input{question:str ,question_type:bool}
            output{dic:dict} dict:{qword:str,new_question:str,product:list,evalueation:list,component:list,brand:list
            is_contrast:bool}


3.4 retrieval:






