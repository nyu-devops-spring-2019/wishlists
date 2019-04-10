#NYU-Travis.ci

[![Build Status](https://travis-ci.com/nyu-devops-spring-2019/wishlists.svg?branch=master)](https://travis-ci.com/nyu-devops-spring-2019/wishlists)

# wishlists
Developing a Wishlist micro service as part of building a e-commerce service for NYU Devops Spring 2019 class

## Prerequisite Installation using Vagrant

The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have this software the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Then all you have to do is clone this repo and invoke vagrant:

    git clone https://github.com/nyu-devops-spring-2019/wishlists
    cd wishlists
    vagrant up
    vagrant ssh
    cd /vagrant

You can now run `nosetests` to run the tests. As developers we always want to run the tests before we change any code so that we know if we brike the code or perhaps someone before us did? Always run the test cases first!

## Manually running the Tests

Run the tests using `nose`

    $ nosetests
