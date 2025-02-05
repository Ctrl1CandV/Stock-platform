# 模拟证券交易平台前端项目

front/
├── node_modules/      		 # 项目依赖的第三方库
├── public/               			# 静态资源目录，不会被 Vite 处理
│   └── vite.svg
├── src/                   			 # 源代码目录
│   ├── assets/            		     # 静态资源目录，会被 Vite 处理
│   │   └── react.svg 
│   ├── components/        	     # Vue 组件目录
│   │   └── HelloWorld.vue # Vue 组件文件
│   ├── App.vue            		  # 主应用组件
│   ├── main.ts          		     # 应用入口文件
│   ├── style.css
│   └── vite-env.d.ts      		# Vite 环境类型声明文件
├── index.html            		  # 应用的 HTML 入口文件
├── package.json         		 # 项目配置文件，包含依赖和脚本
├── package-lock.json      	   # 锁定项目依赖的版本号
├── tsconfig.json         		 # TypeScript 配置文件
├── tsconfig.node.json		# Node.js 环境的 TypeScript 配置文件
├── tsconfig.app.json     	     # 前端应用的 TypeScript 配置文件
├── vite.config.ts         		# Vite 配置文件
└── README.md 