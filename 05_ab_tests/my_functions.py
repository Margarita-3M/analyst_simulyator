def get_smoothed_ctr(user_likes, user_views, global_ctr, alpha):
    '''
    Функция рассчитывает сглаженный CTR.
    ---
    Параметры:
        user_likes -- количество лайков
        user_views -- количество просмотров
        global_ctr -- средний (глобальный) CTR до сглаживания
        alpha      -- значение штрафа
    
    '''
    smoothed_ctr = (user_likes + alpha * global_ctr) / (user_views + alpha) * 100
    return smoothed_ctr

def run_t_test(df=df, metric='smoothed_ctr', exp_gr_1=2, exp_gr_2=3, num_experiments=10000, n_samples=500):
    '''
    Функция формирует подвыборки с повторением из указанного количества наблюдений
    из каждой эспериментальной группы, проводит сравнение этих подвыборок t-testом и возвращает p-values.
    ---
    Параметры:
        df               -- датафрейм
        metric           -- ключевая метрика, по которой ведем расчет
        exp_gr_1         -- номер (int) экспериментальной группы 1
        exp_gr_2         -- номер (int) экспериментальной группы 2
        num_experiments  -- количество экспериментов в симуляции
        n_samples        -- размер подвыборки    
    
    '''
    p_values = []
    exp_gr_1 = df.loc[df['exp_group']==exp_gr_1, metric]
    exp_gr_2 = df.loc[df['exp_group']==exp_gr_2, metric]
    
    for i in range(num_experiments):       
        sample_exp_gr_1 = exp_gr_1.sample(n=n_samples, replace=True).values        
        sample_exp_gr_2 = exp_gr_2.sample(n=n_samples, replace=True).values        
        p_value = stats.ttest_ind(sample_exp_gr_1, sample_exp_gr_2, equal_var=False).pvalue # Welch’s t-test     
        p_values.append(p_value)
    
    p_values_series = pd.Series(p_values)
    return p_values_series

def run_mu_test(df=df, metric='smoothed_ctr', exp_gr_1=2, exp_gr_2=3, num_experiments=10000, n_samples=500):
    '''
    Функция формирует подвыборки с повторением из указанного количества наблюдений
    из каждой эспериментальной группы, проводит сравнение этих подвыборок Mann-Whitney U test и возвращает p-values.
    ---
    Параметры:
        df               -- датафрейм
        metric           -- ключевая метрика, по которой ведем расчет
        exp_gr_1         -- номер (int) экспериментальной группы 1
        exp_gr_2         -- номер (int) экспериментальной группы 2
        num_experiments  -- количество экспериментов в симуляции
        n_samples        -- размер подвыборки    
    
    '''
    p_values = []
    exp_gr_1 = df.loc[df['exp_group']==exp_gr_1, metric]
    exp_gr_2 = df.loc[df['exp_group']==exp_gr_2, metric]
    
    for i in range(num_experiments):       
        sample_exp_gr_1 = exp_gr_1.sample(n=n_samples, replace=True).values        
        sample_exp_gr_2 = exp_gr_2.sample(n=n_samples, replace=True).values        
        p_value = stats.mannwhitneyu(sample_exp_gr_1, sample_exp_gr_2).pvalue     
        p_values.append(p_value)
    
    p_values_series = pd.Series(p_values)
    return p_values_series

def get_bootstrap_ci_ctr(df, num_experiments=1000, alpha=0.05):
    '''
    Функция считает доверительный интервал CTR (двусторонний) при помощи бутстрэпа.
    ---
    Параметры:
        df               -- датафрейм
        num_experiments  -- количество экспериментов в симуляции
        alpha            -- уровень значимости  
    
    '''
    # формируем выборку CTR
    global_ctr_data = []
    for i in range(num_experiments):
        sample = df.sample(frac=0.5, replace=True)
        global_ctr = sample['likes'].sum() / sample['views'].sum()
        global_ctr_data.append(global_ctr)
    
    # рассчитываем границы доварительного интервала
    ci = np.percentile(global_ctr_data, [100 * alpha / 2.0, 100 * (1 - alpha / 2.0)])
    
    return ci

def get_bootstrap_ci_views(df, num_experiments=1000, alpha=0.05):
    '''
    Функция считает доверительный интервал CTR (двусторонний) при помощи бутстрэпа.
    ---
    Параметры:
        df               -- датафрейм
        num_experiments  -- количество экспериментов в симуляции
        alpha            -- уровень значимости  
    
    '''
    # формируем выборку CTR
    global_views_data = []
    for i in range(num_experiments):
        sample = df.sample(frac=0.5, replace=True)
        global_views = sample['views'].mean()
        global_views_data.append(global_views)
    
    # рассчитываем границы доварительного интервала
    ci = np.percentile(global_views_data, [100 * alpha / 2.0, 100 * (1 - alpha / 2.0)])
    
    return ci
