
I'm going to walk through steps to set up an AWS EC2 instance with a python setup and then run a Bokeh server from it. Below are the initial/basic steps:

- Set up AWS account. This is straight forward.

- Set up a EC2 instance. There are a lot of options interms of processors and operating systems. Linux stuff is cheaper, I usually do an ubuntu setup. And if your first time or not doing anything super serious a t2.micro or .nano seems fine.

- Key step is to SSH into the instance from the command prompt. HEre are somelinks that helped me. Note that if you have GIT installed, then you proably have the ssh commands to log into the instance.

https://medium.com/@GalarnykMichael/aws-ec2-part-2-ssh-into-ec2-instance-c7879d47b6b2

https://hackernoon.com/aws-ec2-part-3-installing-anaconda-on-ec2-linux-ubuntu-dbef0835818a

- An important step was to set up the security protocol so my computer could log in. I clicked on the security setup, said my ip and it put in automatically my ip.

- A key file is provided for you to authinticate the log in. Place this in an folder for which only you have access otherwise when you try and ssh in, it my reject the log in attempt bc you are using what is viewed as a "public key"

- Once you have this all setup, below is the SSH part and how to log in: ```ssh -i mykey.pem ubuntu@public_DNS``` where the first part is my key, the next is username which is associated with the installation type, then the last part is the public DNS which you can copy from the instance information on the AWS dashboard. **NOTE** on the EC2 dashboard in the upper right corner is a ``connect`` button that describes more about how to ssh into the instance.

- Onece you log in you should see like a linux command prompt/terminal window. The hard part for me is to implement linux commands (which I know nothing about).

---

Once this is done, the next step is to verify that you have (i) ``git`` which will help you manage and connect with your code from elsewhere and then (ii) set up a minimal instalation of python.

- so type ``git --version`` which should verify that git is installed.

- Then in the ubuntu command line I downloaded the anaconda package I want, (miniconda linux) so I went ``` wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh``` and hit enter, then everything went through.

- Then I typed ```bash Miniconda3-latest-Linux-x86_64.sh``` and then followed the instructions on the screen. After this close the window, then reconnect.

-  Remember miniconda is very striped down. So if you want, say ipython, just do ``pip install ipython`` For the code to run, you probably need to install the different packages, so in my case, pandas, bokeh, and then pyarrow.

---

Two final issues. The ports/security setting need to be setup so that they can be accessed publicly. This took forever for me to figure out. So this is the way it works:

- Bokeh is normally going to display the thing on the port ``5006`` so you need to tell the instance to allow access on that port. So you go into security setings, and go "custom TCP" and then in the port put in ``5006`` and this should take care of it.

- Then to run bokeh you specify the command ``bokeh serve --show main.py --allow-websocket-origin public_DNS:5006`` which will show the figure on the specified port. **NOTE** my only open issue is that it will only show it as ``http`` not ``https`` which does not quite play well with the iframe's I'm using in the webiste.
