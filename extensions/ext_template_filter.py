
def init_app(app):

    # 定义模板过滤器
    @app.template_filter('document_status')
    def document_status_filter(value):
        status_map = {
            'init': ('初始化', 'bg-blue-200 text-blue-600'),
            'indexing': ('索引中', 'bg-orange-200 text-orange-600'),
            'error': ('异常', 'bg-red-200 text-red-600'),
            'completed': ('完成', 'bg-green-200 text-green-600')
        }
        return status_map.get(value, ('未知状态', 'bg-gray-200 text-gray-600'))


