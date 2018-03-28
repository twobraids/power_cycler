# Router Power Cycler

Here's the problem. I've got Comcast as my ISP, but my Comcast router is really flakey. While its administrative Web interface may work just fine, it really isn't connecting to the Internet. The solution to the problem is just power cycling the router.

While that sounds simple, the trouble is that my router is about a mile away from my home. Comcast wouldn't bridge that last mile without requiring I pay several tens of thousands of dollars. So I rent a shelf over in the subdivision a mile from my home, and Comcast puts my point of presence there. I use a microwave link to cover that last mile to my home. Power cycling my router means going a mile and, perhaps, waking my neighbor.

I need to be able to remotely power cycle my router. This code is a key component in using the Things Gateway from Mozilla to automate power cycling my router.

I think of it like this: I make a virtual thing to add to my things gateway that's really just a service running on a computer on my local area network. That service uses the Web Of Things API to make it look to the Things Gateway just like a physical device. The service checks to see if it can see a Web site somewhere outside my network. If it cannot, it raises a ```RouterDownEvent``` event. The Things Gateway, on seeing this event, invokes a rule telling a TP-Link Smart Plug to turn off the power to the router. The service, meanwhile, has started a timer. When the timer expires, it raises another event, ```RestartRouterEvent```. This triggers another rule on the Things Gateway that causes the TP-Link Smart Plug to turn the router back on. Then, after sleeping a while longer, the service goes back to monitoring the remote Web site.

My neighbor will thank me.
