// Jenkinsfile
pipeline {
    // 1. 定义执行代理 (Agent)
    // 'any': 表示在任何可用的 agent 上运行。
    // 你也可以指定特定标签的 agent: agent { label 'my-python-agent' }
    // 或使用 Docker agent: agent { docker { image 'python:3.10-slim' } } (需要 Docker Pipeline 插件)
    agent any

    // 2. (可选) 全局工具配置
    // 如果你在 Jenkins -> Global Tool Configuration 中配置了 Allure Commandline
    tools {
        // 'Default Allure' 是你在 Jenkins Tools 中为 Allure Commandline 设置的名字
         allure 'Default Allure'
    }

    // 3. 定义环境变量 (可选)
    // environment {
    //     // 例如，如果需要设置特定配置文件的路径或凭证 ID
    //     CONFIG_FILE = 'config/config.prod.yaml'
    //     MY_API_TOKEN = credentials('jenkins-api-token-id')
    // }

    // 4. 定义流水线阶段 (Stages)
    stages {
        // 阶段 1: 清理工作空间 (推荐)
        stage('Cleanup Workspace') {
            steps {
                // 使用 Workspace Cleanup 插件清理工作区
                cleanWs()
                echo 'Workspace cleaned.'
            }
        }

        // 阶段 2: 代码检出 (Checkout)
        stage('Checkout Code') {
            steps {
                // 从版本控制系统 (SCM) 检出代码，需要在 Jenkins Job 配置中设置 Git 仓库地址
                echo 'Checking out code...'
                checkout scm
                echo 'Code checkout complete.'
            }
        }

        // 阶段 3: 设置 Python 环境和安装依赖
        stage('Setup Environment') {
            steps {
                script {
                    // 判断操作系统以使用正确的命令 (sh for Linux/macOS, bat for Windows)
                    if (isUnix()) {
                        sh '''
                            echo "Setting up Python virtual environment on Unix-like system..."
                            python -m venv venv
                            # 激活 venv 并安装依赖 (在同一个 sh 块中激活才有效)
                            # 或者直接使用 venv 内的 python/pip 路径，更可靠
                            ./venv/bin/pip install --upgrade pip
                            ./venv/bin/pip install -r requirements.txt
                            echo "Dependencies installed."
                        '''
                    } else {
                        bat '''
                            echo "Setting up Python virtual environment on Windows..."
                            python -m venv venv
                            .\\venv\\Scripts\\pip install --upgrade pip
                            .\\venv\\Scripts\\pip install -r requirements.txt
                            echo "Dependencies installed."
                        '''
                    }
                }
            }
        }

        // 阶段 4: 运行 Pytest 测试
        stage('Run API Tests') {
            steps {
                 script {
                     // 使用 venv 中的 pytest 运行测试，并指定 allure 结果目录
                     def allureResultsDir = 'allure-results'
                     if (isUnix()) {
                         sh "./venv/bin/pytest api_tests --alluredir=${allureResultsDir} --clean-alluredir"
                     } else {
                         bat ".\\venv\\Scripts\\pytest api_tests --alluredir=${allureResultsDir} --clean-alluredir"
                     }
                 }
            }
        }
    } // stages 结束

    // 5. 构建后操作 (Post Actions)
    // 无论构建成功、失败或不稳定，都尝试生成 Allure 报告
    post {
        always {
            echo 'Archiving Allure results and generating report...'
            // 使用 Allure Jenkins 插件提供的 allure 步骤
            // 'allure-results' 是 pytest 命令中 --alluredir 指定的目录
            allure([
                includeProperties: false,
                // jdk: '', // 如果需要特定JDK可指定
                reportBuildPolicy: 'ALWAYS', // 即使构建失败也生成报告
                results: [[path: 'allure-results']] // 指定 Allure 结果目录
            ])
            echo 'Allure report generation step added.'
        }

        // 可以添加成功、失败时的其他操作，如发送通知
        // success {
        //     echo 'Build successful!'
        //     // mail to: 'team@example.com', subject: 'Build Success...'
        // }
        // failure {
        //     echo 'Build failed.'
        //     // mail to: 'team@example.com', subject: 'Build FAILED...'
        // }
    } // post 结束

} // pipeline 结束