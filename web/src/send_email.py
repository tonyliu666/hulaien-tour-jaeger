from flask_mail import Mail,Message
class SendEmail(list):
    #pack[0] = Email , pack[1] = tour
    def send_email(self,pack):
        #pack = [app,tour,Email]
        #可以用kubernetes的secret去做
        # print("receiver",pack[0],sys.stderr)
        # print("url_list",pack[1],sys.stderr)
        pack[0].config['MAIL_SERVER'] = 'smtp.gmail.com'
        pack[0].config['MAIL_PORT'] = 465 
        pack[0].config['MAIL_USERNAME'] = "a0979277212@gmail.com" #使用者名稱
        pack[0].config['MAIL_PASSWORD'] = "smsugjnbylfyefvm"  #使用者密碼(避免兩段式驗證)，需先註冊後使用
        pack[0].config['MAIL_USE_TLS'] = False 
        pack[0].config['MAIL_USE_SSL'] = True
        mail = Mail(pack[0])
        topic = open('./web/src/templates/email_tour.html').read()
        topic = topic.replace('{{first_tag}}',pack[1][0]).replace('{{second_tag}}',pack[1][1]).replace('{{third_tag}}',pack[1][2]).replace('{{fourth_tag}}',pack[1][3]).replace('{{fifth_tag}}',pack[1][4])
        subject = "為您精心挑選的旅遊指南"
        message = Message(subject,sender = "a0979277212@gmail.com",recipients=[pack[2]])
        message.html = topic
        mail.send(message)
    def __init__(self,pack):
        self.pack = pack 
class Value():
    string = ""
    def Value_back():
        return Value.string
