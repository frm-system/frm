import unittest
import os


def main():
    from init import init
    init()
    directory = os.path.dirname(__file__)
    all_tests = unittest.TestLoader().discover(directory)
    unittest.TextTestRunner().run(all_tests)

def main_junit():
    from init import init
    init()

    import xmlrunner
    directory = os.path.dirname(__file__)
    all_tests = unittest.TestLoader().discover(directory)
    xmlrunner.XMLTestRunner(output='test-reports').run(all_tests)


if __name__ == '__main__':
    main()
