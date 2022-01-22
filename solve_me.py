from http.server import BaseHTTPRequestHandler, HTTPServer


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            self.completed_items = file.readlines()
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args, shifted = False):
        priority,task = int(args[0]), args[1]
        if priority in self.current_items.keys():
            #Priority already exists
            already = self.current_items[priority]
            self.current_items[priority] = task
            newPriority = priority+1
            self.add([newPriority, already], True)
            
        else :
            #Priority does not exist
            self.current_items[priority] = task
            self.write_current()

        if shifted == False :
            print(f"Added task: \"{task}\" with priority {str(priority)}")
        

    def done(self, args):
        priority = int(args[0])
        if priority in self.current_items.keys() :
            self.completed_items.append(self.current_items[priority])
            del self.current_items[priority]
            print('Marked item as done.')
        else :
            print(f"Error: no incomplete item with priority {priority} exists.")
        
        self.write_completed()
        self.write_current()

    def delete(self, args):
        priority = int(args[0])
        if priority in self.current_items.keys() :
            del self.current_items[priority]
            print(f"Deleted item with priority {priority}")
        else :
            print(f"Error: item with priority {priority} does not exist. Nothing deleted.")
        
        self.write_current()

    def ls(self):
        i = 0
        for task in self.current_items:
            i+=1
            print(f"{i}. {self.current_items[task]} [{task}]")


    def report(self):
        print(f"Pending : {len(self.current_items)}")
        self.ls()
        print(f"\nCompleted : {len(self.completed_items)}")
        i = 0
        for i in range(len(self.completed_items)):
            print(f"{i+1}. {self.completed_items[i]}")

    def render_pending_tasks(self):
        # Complete this method to return all incomplete tasks as HTML
        outPut = self.getStyle()
        outPut += '<div class="t-wrap"><h1>Pending Tasks:</h1><ol>'
        for task in self.current_items:
            outPut += f'<li class="t-ls">{self.current_items[task]} [{task}]</li>'
        outPut += '</ol><a href="completed">See Completed Tasks</button></a>'
        return outPut

    def render_completed_tasks(self):
        # Complete this method to return all completed tasks as HTML
        self.read_completed()
        outPut = self.getStyle()
        outPut += '<div class="t-wrap"><h1>Completed Tasks:</h1><ol>'
        i = 0
        for i in range(len(self.completed_items)):
            outPut += f'<li class="t-ls">{self.completed_items[i]}</li>'
        outPut += '</ol><a href="tasks">See Incomplete Tasks</button></a>'
        return outPut

    def getStyle(self) :
        return '''
            <style>
                html, body{
                    margin:0px;
                    padding:0px;
                }
                .t-wrap{
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    height:100vh;
                    flex-direction:column;
                }
                ol{
                    width:200px;
                }
                .t-ls{
                    padding:10px;
                    border-radius:10px;
                }
                a{
                    padding:15px 40px;
                    border-radius:8px;
                    background:dodgerblue;
                    border:0px;
                    color:white;
                    cursor:pointer;
                    text-decoration:none;
                    transition:0.2s;
                }
                a:hover{
                    background:purple;
                }
            </style>
        '''

class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())
